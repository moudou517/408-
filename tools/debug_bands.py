# -*- coding: utf-8 -*-
"""Why does band detection fail on some years? Print raw line starts."""

import os
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_figures import pdf_of

for year in sys.argv[1:] or ["2020", "2016", "2018"]:
    p = pdf_of(year)
    print("=" * 90)
    print(year, p)
    doc = pymupdf.open(p)
    page = doc[0]
    d = page.get_text("dict")
    n = 0
    for blk in d.get("blocks", []):
        if blk.get("type") != 0:
            continue
        for line in blk.get("lines", []):
            txt = "".join(s.get("text", "") for s in line.get("spans", []))
            if not txt.strip():
                continue
            y = line["bbox"][1]
            print(f"  y={y:6.1f}  {txt[:56]!r}")
            n += 1
            if n >= 12:
                break
        if n >= 12:
            break
    doc.close()
