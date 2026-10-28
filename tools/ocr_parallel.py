"""OCR the garbled-font exam PDFs using a process pool (one worker per PDF).

Each worker caps BLAS/ORT threads so 7 workers do not thrash a 32-core box.
"""

import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "3")
os.environ.setdefault("ORT_NUM_THREADS", "3")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "3")

ROOT = r"E:\CST\408"
TEXTOUT = os.path.join(ROOT, "work", "text")
IMGOUT = os.path.join(ROOT, "work", "pages")
os.makedirs(TEXTOUT, exist_ok=True)
os.makedirs(IMGOUT, exist_ok=True)


def find_pdf(year):
    for dirpath, _d, files in os.walk(ROOT):
        if ".pylibs" in dirpath or ".tmp" in dirpath or os.sep + "work" in dirpath:
            continue
        for f in files:
            if f.lower().endswith(".pdf") and str(year) in f:
                return os.path.join(dirpath, f)
    return None


def ocr_one(year):
    import numpy as np
    import pymupdf
    from PIL import Image
    from rapidocr_onnxruntime import RapidOCR

    path = find_pdf(year)
    if not path:
        return f"{year}: PDF not found"
    base = os.path.basename(path).replace(".pdf", "")
    dest = os.path.join(TEXTOUT, base + ".ocr.txt")
    if os.path.exists(dest) and not os.environ.get("FORCE"):
        return f"{year}: skip (exists)"

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

    ocr = RapidOCR()
    parts = [f"# source: {path}", f"# pages: {npages}", "# engine: rapidocr_onnxruntime"]
    for i, im in enumerate(imgs):
        Image.fromarray(im[:, :, ::-1]).save(
            os.path.join(IMGOUT, f"{base}_p{i+1:02d}.png")
        )
        try:
            res, _ = ocr(im)
        except Exception as e:
            parts.append(f"\n<<<PAGE {i+1}>>>  [OCR ERROR {type(e).__name__}]")
            continue
        lines = []
        if res:
            rows = sorted(res, key=lambda r: (round(min(p[1] for p in r[0]) / 12), min(p[0] for p in r[0])))
            lines = [r[1] for r in rows if r[2] > 0.45]
        parts.append(f"\n<<<PAGE {i+1}>>>")
        parts.extend(lines)
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return f"{year}: {npages} pages in {time.time()-t0:.0f}s -> {os.path.basename(dest)}"


if __name__ == "__main__":
    years = sys.argv[1:] or ["2009", "2010", "2013", "2015", "2016", "2018", "2023"]
    from concurrent.futures import ProcessPoolExecutor, as_completed

    with ProcessPoolExecutor(max_workers=min(7, len(years))) as ex:
        futs = {ex.submit(ocr_one, y): y for y in years}
        for fut in as_completed(futs):
            y = futs[fut]
            try:
                print(fut.result(), flush=True)
            except Exception as e:
                print(f"{y}: FAILED {type(e).__name__}: {e}", flush=True)
    print("all done", flush=True)
