# -*- coding: utf-8 -*-
"""OCR the answer-table page of each 解析 PDF and recover the 40 MCQ answers.

The printed question numbers are the anchor, so the result is self-validating:
every recovered pair is (number printed in the doc -> letter printed next to it).
"""

import glob
import json
import os
import re
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "4")

ROOT = r"E:\CST\408"
ANS_TXT = os.path.join(ROOT, "work", "text_ans")
os.makedirs(ANS_TXT, exist_ok=True)

PAIR = re.compile(r"(?<!\d)(\d{1,2})\s*[.．、)）]?\s*([A-D])(?![A-Za-z])")
JUNK = re.compile(r"(?:第|共|页|年|月|分|解析|答案|选择|题)")


def pdf_of(year):
    for p in glob.glob(os.path.join(ROOT, "*真题解析.pdf")):
        m = re.search(r"(19|20)\d{2}", os.path.basename(p))
        if m and m.group(0) == str(year):
            return p
    return None


def ocr_pages(path, pages, dpi=200):
    import numpy as np
    import pymupdf
    from rapidocr_onnxruntime import RapidOCR

    doc = pymupdf.open(path)
    out = []
    for pi in pages:
        if pi >= len(doc):
            continue
        pm = doc[pi].get_pixmap(dpi=dpi)
        a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
        if pm.n == 4:
            a = a[:, :, :3]
        out.append((pi, a[:, :, ::-1].copy()))
    doc.close()

    cfg = os.path.join(ROOT, "work", "ocr_config.yaml")
    ocr = RapidOCR(config_path=cfg) if os.path.exists(cfg) else RapidOCR()
    res = []
    for pi, img in out:
        try:
            r, _ = ocr(img)
        except Exception as e:
            print(f"    p{pi+1} OCR error {type(e).__name__}", flush=True)
            continue
        lines = []
        if r:
            rows = sorted(r, key=lambda x: (round(min(p[1] for p in x[0]) / 12),
                                           min(p[0] for p in x[0])))
            lines = [x[1] for x in rows if x[2] > 0.4]
        res.append((pi, "\n".join(lines)))
    return res


def answers_from_text(txt):
    """First occurrence per question number, restricted to 1..40."""
    ans, order = {}, []
    for m in PAIR.finditer(txt):
        q, ch = int(m.group(1)), m.group(2)
        if not (1 <= q <= 40):
            continue
        if q in ans:
            continue
        ans[q] = ch
        order.append(q)
    return ans


def main():
    years = [int(x) for x in sys.argv[1:]] or list(range(2009, 2027))
    out = {}
    if os.path.exists(os.path.join(ROOT, "work", "answers.json")):
        out = json.load(open(os.path.join(ROOT, "work", "answers.json"), encoding="utf-8"))

    for y in years:
        p = pdf_of(y)
        if not p:
            print(f"{y}: no pdf")
            continue
        t0 = time.time()
        got = None
        for pages in ([0], [0, 1], [0, 1, 2]):
            res = ocr_pages(p, pages)
            txt = "\n".join(t for _, t in res)
            cand = answers_from_text(txt)
            if len(cand) >= 38:
                got = cand
                with open(os.path.join(ANS_TXT, f"{y}_table.ocr.txt"), "w",
                          encoding="utf-8") as f:
                    f.write(txt)
                break
        if got:
            full = {}
            for i in range(1, 41):
                if i in got:
                    full[str(i)] = got[i]
            out[str(y)] = full
            prev = "".join(full.get(str(i), "-") for i in range(1, 21))
            print(f"{y}: {len(full)}/40  ({time.time()-t0:.0f}s)  {prev}...", flush=True)
        else:
            print(f"{y}: FAILED ({time.time()-t0:.0f}s)", flush=True)

    json.dump(out, open(os.path.join(ROOT, "work", "answers.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    tot = sum(len(v) for v in out.values())
    print(f"\nanswers.json: {len(out)} years, {tot} answers")


if __name__ == "__main__":
    main()
