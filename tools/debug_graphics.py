# -*- coding: utf-8 -*-
"""Check graphics inventory for a year's pages (why 0 figures?)."""

import os
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_figures import drawings_on, images_on, pdf_of, question_bands

year = sys.argv[1] if len(sys.argv) > 1 else "2020"
p = pdf_of(year)
doc = pymupdf.open(p)
print(year, p, "pages:", len(doc))
for pi in range(min(6, len(doc))):
    page = doc[pi]
    b = question_bands(page)
    im = images_on(page)
    dr = drawings_on(page)
    raw_imgs = page.get_image_info()
    print(f"  p{pi+1}: bands={len(b)} imgs(filtered)={len(im)} "
          f"imgs(raw)={len(raw_imgs)} drawings={len(dr)}")
    if raw_imgs:
        print("     raw img bboxes:", [tuple(round(v) for v in i['bbox']) for i in raw_imgs[:4]])
    if b:
        print("     bands:", [(q, round(y)) for q, y in b])
doc.close()
