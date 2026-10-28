# -*- coding: utf-8 -*-
"""OCR a whole 解析 PDF whose text layer is empty (2019/2021/2023).

Writes work/text_ans/<year>.ocr.txt so extract_bigq.py can pick it up.
"""

import glob
import os
import re
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "4")

ROOT = r"E:\CST\408"
ANS = os.path.join(ROOT, "work", "text_ans")
os.makedirs(ANS, exist_ok=True)


def pdf_of(year):
    for p in glob.glob(os.path.join(ROOT, "*真题解析.pdf")):
        m = re.search(r"(19|20)\d{2}", os.path.basename(p))
        if m and m.group(0) == str(year):
            return p
    return None


def run(year):
    import numpy as np
    import pymupdf
    from rapidocr_onnxruntime import RapidOCR

    p = pdf_of(year)
    if not p:
        print(f"{year}: no pdf")
        return
    dest = os.path.join(ANS, f"{year}.ocr.txt")
    if os.path.exists(dest) and os.path.getsize(dest) > 4000:
        print(f"{year}: skip (exists)")
        return

    t0 = time.time()
    doc = pymupdf.open(p)
    imgs = []
    for page in doc:
        pm = page.get_pixmap(dpi=180)
        a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
        if pm.n == 4:
            a = a[:, :, :3]
        imgs.append(a[:, :, ::-1].copy())
    n = len(doc)
    doc.close()
    print(f"{year}: {n} pages", flush=True)

    cfg = os.path.join(ROOT, "work", "ocr_config.yaml")
    ocr = RapidOCR(config_path=cfg) if os.path.exists(cfg) else RapidOCR()
    parts = [f"# OCR fallback for {year}", f"# pages: {n}"]
    for i, im in enumerate(imgs):
        try:
            r, _ = ocr(im)
        except Exception as e:
            print(f"  p{i+1} error {type(e).__name__}", flush=True)
            continue
        lines = []
        if r:
            rows = sorted(r, key=lambda x: (round(min(q[1] for q in x[0]) / 12),
                                           min(q[0] for q in x[0])))
            lines = [x[1] for x in rows if x[2] > 0.4]
        parts.append(f"\n<<<PAGE {i+1}>>>")
        parts.extend(lines)
        print(f"  p{i+1}: {len(lines)} lines", flush=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"{year}: DONE {time.time()-t0:.0f}s -> {dest}", flush=True)


if __name__ == "__main__":
    for y in sys.argv[1:]:
        run(y)
