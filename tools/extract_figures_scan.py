# -*- coding: utf-8 -*-
"""Tier B: years whose PDF pages are one full-page scan.

There is no separable figure object, so we crop the *question's slice of the page*
(题干 + 插图) as a 「原卷截图」. Question numbers come from OCR of the left margin
strip only — that strip is small, so this stays fast.
"""

import json
import os
import re
import sys
import time

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
IMG = os.path.join(OUT, "qimg")
os.makedirs(IMG, exist_ok=True)

DPI = 175
MAX_W = 1000        # 切片最大宽度（px），控制总体积
QRE = re.compile(r"(\d{1,2})\s*[.．、]")
# 题干里真正"要看图"的说法（"图论"这类不算）
FIGREF = re.compile(r"(如图|图\s*所示|图中|下图|上图|见图|图示|题\s*\d+\s*图|如题\s*\d+)")


def need_figure_stems():
    """{(year, q)} —— 题干里提到图的题。综合题用完整题干（bigq.json）。"""
    import json as _json
    out = {}
    src = os.path.join(ROOT, "work", "out", "questions.json")
    big = os.path.join(ROOT, "out", "data", "bigq.json")
    stems = {}
    if os.path.exists(src):
        for r in _json.load(open(src, encoding="utf-8")):
            stems[(r["year"], r["q"])] = r.get("stem") or ""
    if os.path.exists(big):
        for r in _json.load(open(big, encoding="utf-8")):
            if r.get("st"):
                stems[(r["y"], r["q"])] = r["st"]     # 综合题：完整题干覆盖短的
    for k, s in stems.items():
        if FIGREF.search(s):
            out[k] = True
    return out


def pdf_of(year):
    hits = []
    for dirpath, _d, files in os.walk(ROOT):
        if ".pylibs" in dirpath or ".tmp" in dirpath or os.sep + "work" in dirpath:
            continue
        for f in files:
            if not f.lower().endswith(".pdf") or "解析" in f:
                continue
            m = re.search(r"(19|20)\d{2}", f)
            if m and m.group(0) == str(year):
                hits.append(os.path.join(dirpath, f))
    return hits[0] if hits else None


def main():
    years = [int(x) for x in sys.argv[1:]] or [2009, 2010, 2013, 2015, 2016, 2018, 2020, 2023]
    import numpy as np
    import pymupdf
    from PIL import Image
    from rapidocr_onnxruntime import RapidOCR

    cfg = os.path.join(ROOT, "work", "ocr_config.yaml")
    ocr = RapidOCR(config_path=cfg) if os.path.exists(cfg) else RapidOCR()

    dest_json = os.path.join(OUT, "data", "figures.json")
    figures = {}
    if os.path.exists(dest_json):
        figures = json.load(open(dest_json, encoding="utf-8"))
    # 归一化旧格式
    for k, v in list(figures.items()):
        if isinstance(v, str):
            figures[k] = {"p": v, "scan": False}

    for year in years:
        p = pdf_of(year)
        if not p:
            print(f"{year}: no pdf")
            continue
        t0 = time.time()
        doc = pymupdf.open(p)
        n_ok = 0
        for pi, page in enumerate(doc):
            pm = page.get_pixmap(dpi=DPI)
            arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
            if pm.n == 4:
                arr = arr[:, :, :3]
            rgb = arr[:, :, ::-1]                      # PIL 用 RGB
            H, W = rgb.shape[:2]
            # 左侧页边窄条：题号所在区域
            x0, x1 = int(W * 0.03), int(W * 0.34)
            strip = rgb[:, x0:x1][:, :, ::-1].copy()   # rapidocr 用 BGR
            try:
                res, _ = ocr(strip)
            except Exception as e:
                print(f"  {year} p{pi+1} ocr fail {type(e).__name__}")
                continue
            marks = []
            for box, text, score in (res or []):
                if score < 0.4:
                    continue
                m = QRE.match(text.strip())
                if not m:
                    continue
                q = int(m.group(1))
                if not (1 <= q <= 47):
                    continue
                ys = [pt[1] for pt in box]
                marks.append((q, min(ys)))
            marks.sort(key=lambda t: t[1])
            seen, uniq = set(), []
            for q, y in marks:
                if q in seen:
                    continue
                seen.add(q)
                uniq.append((q, y))
            if not uniq:
                continue
            for i, (q, y) in enumerate(uniq):
                key = f"{year}-{q}"
                if key in figures and figures[key].get("scan"):
                    continue
                y_end = uniq[i + 1][1] if i + 1 < len(uniq) else H
                top = max(0, int(y) - 12)
                bot = min(H, int(y_end) - 4)
                if bot - top < 40:
                    continue
                dest = os.path.join(IMG, f"{year}_{q}.png")
                crop = Image.fromarray(rgb[top:bot, :])
                if crop.width > MAX_W:                  # 降采样，控制体积
                    ratio = MAX_W / crop.width
                    crop = crop.resize((MAX_W, max(1, int(crop.height * ratio))),
                                       Image.LANCZOS)
                crop.save(dest, optimize=True)
                figures[key] = {"p": f"qimg/{year}_{q}.png", "scan": True}
                n_ok += 1
        doc.close()
        print(f"{year}: 切片 {n_ok} 张 ({time.time()-t0:.0f}s)", flush=True)

    json.dump(figures, open(dest_json, "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    scan = sum(1 for v in figures.values() if v.get("scan"))
    print(f"\nfigures.json: 共 {len(figures)} 条（原卷切片 {scan}）")


if __name__ == "__main__":
    main()
