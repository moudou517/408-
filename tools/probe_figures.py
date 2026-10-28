# -*- coding: utf-8 -*-
"""Feasibility probe: can we locate and crop the figure that a question refers to?

For a page, look at:
  * raster images (bbox known)
  * vector drawings (bbox known)
  * text spans  -> find "tN N 图" / "图所示" references and their position
Then check whether a graphic cluster sits next to the reference.
"""

import glob
import os
import re
import sys

import pymupdf

ROOT = r"E:\CST\408"
year = sys.argv[1] if len(sys.argv) > 1 else "2024"


def pdf_of(year):
    for p in glob.glob(os.path.join(ROOT, "**", "*.pdf"), recursive=True):
        if ".pylibs" in p:
            continue
        b = os.path.basename(p)
        m = re.search(r"(19|20)\d{2}", b)
        if m and m.group(0) == str(year) and "解析" not in b:
            return p
    return None


p = pdf_of(year)
print("pdf:", p)
doc = pymupdf.open(p)
print("pages:", len(doc))

for pi in range(min(4, len(doc))):
    page = doc[pi]
    imgs = page.get_image_info()
    draws = page.get_drawings()
    txt = page.get_text("text")
    refs = re.findall(r"题\s*(\d{1,2})\s*图|如(?:下|上)?图|图\s*(\d{1,2})", txt)
    print(f"\n=== page {pi+1} ===")
    print("  raster images:", len(imgs),
          [tuple(round(v) for v in i["bbox"]) for i in imgs[:6]])
    print("  vector drawings:", len(draws))
    if draws:
        boxes = [tuple(round(v) for v in d["rect"]) for d in draws[:8]]
        print("   sample draw rects:", boxes)
    print("  figure refs:", refs[:6])
doc.close()
