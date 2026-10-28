"""Render PDF pages to PNG and OCR them with RapidOCR (Chinese).

Writes per-PDF transcript files and a page-image cache.
"""

import os
import sys

import numpy as np
import pymupdf
from PIL import Image

ROOT = r"E:\CST\408"
TEXTOUT = os.path.join(ROOT, "work", "text")
IMGOUT = os.path.join(ROOT, "work", "pages")
os.makedirs(TEXTOUT, exist_ok=True)
os.makedirs(IMGOUT, exist_ok=True)


def find_pdfs():
    out = []
    for dirpath, _d, files in os.walk(ROOT):
        if ".pylibs" in dirpath or ".tmp" in dirpath or "work" in dirpath:
            continue
        for f in files:
            if f.lower().endswith(".pdf"):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def render(path, dpi=200):
    doc = pymupdf.open(path)
    imgs = []
    for i, page in enumerate(doc):
        pm = page.get_pixmap(dpi=dpi)
        img = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
        if pm.n == 4:
            img = img[:, :, :3]
        imgs.append(img[:, :, ::-1].copy())  # RGB -> BGR for rapidocr
    n = len(doc)
    doc.close()
    return imgs, n


def main():
    targets = sys.argv[1:]
    pdfs = find_pdfs()
    if targets:
        pdfs = [p for p in pdfs if any(t in os.path.basename(p) for t in targets)]
    print(f"processing {len(pdfs)} PDFs\n", flush=True)

    from rapidocr_onnxruntime import RapidOCR

    ocr = RapidOCR()

    for p in pdfs:
        base = os.path.basename(p).replace(".pdf", "")
        dest = os.path.join(TEXTOUT, base + ".ocr.txt")
        if os.path.exists(dest) and not os.environ.get("FORCE"):
            print(f"skip (exists) {base}", flush=True)
            continue
        try:
            imgs, npages = render(p)
        except Exception as e:
            print(f"RENDER FAIL {base}: {type(e).__name__}: {e}", flush=True)
            continue
        print(f"[{base}] {npages} pages", flush=True)
        parts = [f"# source: {p}", f"# pages: {npages}", f"# engine: rapidocr_onnxruntime"]
        for i, im in enumerate(imgs):
            Image.fromarray(im[:, :, ::-1]).save(
                os.path.join(IMGOUT, f"{base}_p{i+1:02d}.png")
            )
            try:
                res, _ = ocr(im)
            except Exception as e:
                print(f"  p{i+1} OCR FAIL {type(e).__name__}: {e}", flush=True)
                res = None
            lines = []
            if res:
                # res rows: [box, text, score]
                ordered = sorted(res, key=lambda r: (min(pt[1] for pt in r[0]),
                                                     min(pt[0] for pt in r[0])))
                lines = [r[1] for r in ordered if r[2] > 0.5]
            parts.append(f"\n<<<PAGE {i+1}>>>")
            parts.extend(lines)
            print(f"  p{i+1}: {len(lines)} lines", flush=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))
        print(f"  -> {dest}", flush=True)


if __name__ == "__main__":
    main()
