"""OCR one garbled-font exam PDF. Called as: python ocr_worker.py <year>"""

import os
import re
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("ORT_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")

ROOT = r"E:\CST\408"
TEXTOUT = os.path.join(ROOT, "work", "text")
IMGOUT = os.path.join(ROOT, "work", "pages")


def find_pdf(year):
    hits = []
    for dirpath, _d, files in os.walk(ROOT):
        if ".pylibs" in dirpath or ".tmp" in dirpath or (os.sep + "work") in dirpath:
            continue
        for f in files:
            if not f.lower().endswith(".pdf"):
                continue
            m = re.search(r"(19|20)\d{2}", f)
            if m and m.group(0) == str(year):
                hits.append(os.path.join(dirpath, f))
    return hits[0] if hits else None


def run(year):
    import numpy as np
    import pymupdf
    from PIL import Image
    from rapidocr_onnxruntime import RapidOCR

    os.makedirs(TEXTOUT, exist_ok=True)
    os.makedirs(IMGOUT, exist_ok=True)

    path = find_pdf(year)
    if not path:
        print(f"{year}: PDF not found")
        return
    base = os.path.basename(path).replace(".pdf", "")
    dest = os.path.join(TEXTOUT, base + ".ocr.txt")
    if os.path.exists(dest) and len(open(dest, encoding="utf-8").read()) > 3000:
        print(f"{year}: skip (exists)")
        return

    t0 = time.time()
    doc = pymupdf.open(path)
    imgs = []
    for page in doc:
        pm = page.get_pixmap(dpi=180)
        a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)
        if pm.n == 4:
            a = a[:, :, :3]
        imgs.append(a[:, :, ::-1].copy())
    npages = len(doc)
    doc.close()
    print(f"{year}: {npages} pages, dpi=180", flush=True)

    cfg = os.path.join(ROOT, "work", "ocr_config.yaml")
    ocr = RapidOCR(config_path=cfg) if os.path.exists(cfg) else RapidOCR()
    print(f"{year}: engine ready", flush=True)
    parts = [f"# source: {path}", f"# pages: {npages}", "# engine: rapidocr_onnxruntime"]
    for i, im in enumerate(imgs):
        Image.fromarray(im[:, :, ::-1]).save(
            os.path.join(IMGOUT, f"{base}_p{i+1:02d}.png")
        )
        try:
            res, _ = ocr(im)
        except Exception as e:
            parts.append(f"\n<<<PAGE {i+1}>>>  [OCR ERROR {type(e).__name__}]")
            print(f"  p{i+1} ERROR {type(e).__name__}", flush=True)
            continue
        lines = []
        if res:
            rows = sorted(
                res,
                key=lambda r: (round(min(p[1] for p in r[0]) / 14), min(p[0] for p in r[0])),
            )
            lines = [r[1] for r in rows if r[2] > 0.45]
        parts.append(f"\n<<<PAGE {i+1}>>>")
        parts.extend(lines)
        print(f"  p{i+1}: {len(lines)} lines", flush=True)

    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"{year}: DONE {time.time()-t0:.0f}s -> {os.path.basename(dest)}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
