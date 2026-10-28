# -*- coding: utf-8 -*-
"""Recover the 40 MCQ answers by OCR + geometric grid reconstruction.

Pixels carry the layout, so cluster OCR boxes into rows and columns, then pair
each printed question number with the letter printed beside it.  This handles both
5x8 and 8x5 answer grids and tolerates duplicated/false anchors in the 解析 text.
"""

import glob
import json
import os
import re
import sys
import time

ROOT = r"E:\CST\408"
CACHE = os.path.join(ROOT, "work", "ans_boxes")
os.makedirs(CACHE, exist_ok=True)

NUM = re.compile(r"^(\d{1,2})\s*[.．、]?$")
LET = re.compile(r"^([A-D])$")


def pdf_of(year):
    for p in glob.glob(os.path.join(ROOT, "*真题解析.pdf")):
        m = re.search(r"(19|20)\d{2}", os.path.basename(p))
        if m and m.group(0) == str(year):
            return p
    return None


def ocr_boxes(path, pages, dpi=240):
    import numpy as np
    import pymupdf
    from rapidocr_onnxruntime import RapidOCR

    doc = pymupdf.open(path)
    imgs = []
    for pi in pages:
        if pi >= len(doc):
            continue
        pm = doc[pi].get_pixmap(dpi=dpi)
        a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
        if pm.n == 4:
            a = a[:, :, :3]
        imgs.append((pi, a[:, :, ::-1].copy()))
    doc.close()

    cfg = os.path.join(ROOT, "work", "ocr_config.yaml")
    ocr = RapidOCR(config_path=cfg) if os.path.exists(cfg) else RapidOCR()
    out = []
    for pi, img in imgs:
        try:
            res, _ = ocr(img)
        except Exception as e:
            print(f"    p{pi+1} OCR error {type(e).__name__}", flush=True)
            continue
        items = []
        for box, text, score in (res or []):
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            items.append({
                "t": text.strip(), "x": sum(xs) / 4, "y": sum(ys) / 4,
                "x0": min(xs), "s": float(score),
            })
        out.append((pi, items))
    return out


def cluster(vals, tol):
    vals = sorted(vals)
    groups, cur = [], [vals[0]]
    for v in vals[1:]:
        if v - cur[-1] <= tol:
            cur.append(v)
        else:
            groups.append(cur)
            cur = [v]
    groups.append(cur)
    return [sum(g) / len(g) for g in groups]


def grid_answers(items, want=40):
    """Pair numbers with the letter to their right, row by row."""
    nums = [i for i in items if NUM.match(i["t"]) and 1 <= int(re.sub(r"\D", "", i["t"])) <= want]
    lets = [i for i in items if LET.match(i["t"])]
    if len(nums) < want * 0.7 or len(lets) < want * 0.7:
        return {}

    # ignore letter-ish tokens far below the number block (they are body text)
    ymax = max(n["y"] for n in nums) + 40
    lets = [l for l in lets if l["y"] <= ymax]

    rows_v = cluster([n["y"] for n in nums], 14)
    ans = {}
    for rv in rows_v:
        rn = sorted([n for n in nums if abs(n["y"] - rv) <= 14], key=lambda t: t["x"])
        rl = sorted([l for l in lets if abs(l["y"] - rv) <= 14], key=lambda t: t["x"])
        if not rn or not rl:
            continue
        avail = list(rl)
        for n in rn:
            q = int(re.sub(r"\D", "", n["t"]))
            if q in ans:
                continue
            best, bd = None, 1e9
            for l in avail:
                dx = l["x"] - n["x"]
                if dx < -3:
                    continue
                d = abs(dx)
                if d < bd:
                    bd, best = d, l
            if best is not None and bd < 220:
                ans[q] = best["t"]
                avail.remove(best)
    return ans


def main():
    years = [int(x) for x in sys.argv[1:]] or list(range(2009, 2027))
    dest = os.path.join(ROOT, "work", "answers.json")
    out = json.load(open(dest, encoding="utf-8")) if os.path.exists(dest) else {}

    for y in years:
        p = pdf_of(y)
        if not p:
            print(f"{y}: no pdf")
            continue
        t0 = time.time()
        got = {}
        for pages in ([0], [0, 1], [1], [0, 1, 2]):
            cache_f = os.path.join(CACHE, f"{y}_{'_'.join(map(str,pages))}.json")
            if os.path.exists(cache_f):
                items = json.load(open(cache_f, encoding="utf-8"))
            else:
                res = ocr_boxes(p, pages)
                items = []
                for pi, its in res:
                    for it in its:
                        it["p"] = pi
                        items.append(it)
                json.dump(items, open(cache_f, "w", encoding="utf-8"), ensure_ascii=False)
            cand = grid_answers(items)
            if len(cand) > len(got):
                got = cand
            if len(got) >= 40:
                break
        if got:
            out[str(y)] = {str(k): v for k, v in sorted(got.items())}
            prev = "".join(out[str(y)].get(str(i), "-") for i in range(1, 21))
            print(f"{y}: {len(got)}/40 ({time.time()-t0:.0f}s) {prev}...", flush=True)
        else:
            print(f"{y}: FAILED ({time.time()-t0:.0f}s)", flush=True)

    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"\nanswers.json: {len(out)} years, {sum(len(v) for v in out.values())} answers")


if __name__ == "__main__":
    main()
