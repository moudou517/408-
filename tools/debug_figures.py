# -*- coding: utf-8 -*-
"""Debug why figures are missed: print per-page question bands and image bboxes."""

import glob
import os
import re
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_figures import images_on, pdf_of, question_bands

year = sys.argv[1] if len(sys.argv) > 1 else "2024"
pages = [int(x) for x in sys.argv[2:]] or [1, 2, 3]

p = pdf_of(year)
doc = pymupdf.open(p)
for pi in pages:
    if pi > len(doc):
        continue
    page = doc[pi - 1]
    print(f"=== page {pi}  size {page.rect.width:.0f}x{page.rect.height:.0f} ===")
    bands = question_bands(page)
    print("  bands:", [(q, round(y)) for q, y in bands])
    imgs = images_on(page)
    print("  images:", [tuple(round(v) for v in r) for r in imgs])
    draws = page.get_drawings()
    print(f"  drawings: {len(draws)}")
    if bands and imgs:
        page_h = page.rect.height
        for i, (q, y) in enumerate(bands):
            y_end = bands[i + 1][1] if i + 1 < len(bands) else page_h + 1
            inside = [r for r in imgs if (y - 40) <= (r.y0 + r.y1) / 2 <= y_end]
            if inside:
                print(f"    Q{q} [{round(y-40)}..{round(y_end)}] <- {len(inside)} img")
doc.close()
