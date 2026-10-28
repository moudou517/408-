"""Extract text from every 408 exam PDF into per-year UTF-8 text files."""

import os
import re
import sys

import pymupdf

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "work", "text")
os.makedirs(OUT, exist_ok=True)

PDFS = []
for dirpath, _dirnames, filenames in os.walk(ROOT):
    if ".pylibs" in dirpath or ".tmp" in dirpath:
        continue
    for fn in filenames:
        if fn.lower().endswith(".pdf"):
            PDFS.append(os.path.join(dirpath, fn))
PDFS.sort()


def year_of(path):
    m = re.search(r"(19|20)\d{2}", os.path.basename(path))
    return m.group(0) if m else "unknown"


print(f"{len(PDFS)} PDFs\n")
summary = []
for p in PDFS:
    yr = year_of(p)
    tag = os.path.basename(p).replace(".pdf", "")
    try:
        doc = pymupdf.open(p)
        chunks = []
        for i, page in enumerate(doc):
            t = page.get_text("text")
            chunks.append(f"\n<<<PAGE {i+1}>>>\n{t}")
        txt = "".join(chunks)
        npages = len(doc)
        doc.close()
        # crude scan detection: CJK chars per page
        cjk = len(re.findall(r"[\u4e00-\u9fff]", txt))
        per_page = cjk / max(npages, 1)
        is_scan = per_page < 30
        dest = os.path.join(OUT, f"{yr}_{tag.split('_')[0]}.txt" if False else f"{tag}.txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(f"# source: {p}\n# pages: {npages}  cjk: {cjk}  cjk/page: {per_page:.1f}\n")
            f.write(txt)
        summary.append((yr, os.path.basename(p), npages, len(txt), cjk, per_page, is_scan))
    except Exception as e:
        summary.append((yr, os.path.basename(p), -1, 0, 0, 0, True))
        print(f"FAIL {p}: {type(e).__name__}: {e}")

print(f"{'year':<6}{'pages':>6}{'chars':>9}{'cjk':>8}{'cjk/pg':>8}  scan?  file")
for yr, name, npages, nchar, cjk, pp, scan in sorted(summary):
    flag = "YES" if scan else "  no"
    print(f"{yr:<6}{npages:>6}{nchar:>9}{cjk:>8}{pp:>8.1f}  {flag}   {name}")
