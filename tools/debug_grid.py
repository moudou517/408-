# -*- coding: utf-8 -*-
"""Dump word coordinates of the answer-table page to understand the grid layout."""

import glob
import os
import re
import sys

import pymupdf

ROOT = r"E:\CST\408"
year = sys.argv[1] if len(sys.argv) > 1 else "2009"

p = None
for q in glob.glob(os.path.join(ROOT, "*真题解析.pdf")):
    m = re.search(r"(19|20)\d{2}", os.path.basename(q))
    if m and m.group(0) == year:
        p = q
        break
print("pdf:", p)

doc = pymupdf.open(p)
page = doc[0]
print("page size:", page.rect)
words = page.get_text("words")
nums = [w for w in words if re.fullmatch(r"\d{1,2}[.．、]?", w[4].strip())]
lets = [w for w in words if re.fullmatch(r"[A-D]", w[4].strip())]
print(f"words={len(words)}  number-like={len(nums)}  letter-like={len(lets)}")

print("\n-- first 30 number words (x0,y0,x1,y1) --")
for w in nums[:30]:
    print(f"  {w[4]!r:8} x0={w[0]:7.1f} y0={w[1]:7.1f} yc={(w[1]+w[3])/2:7.1f}")
print("\n-- first 30 letter words --")
for w in lets[:30]:
    print(f"  {w[4]!r:4} x0={w[0]:7.1f} y0={w[1]:7.1f} yc={(w[1]+w[3])/2:7.1f}")

print("\n-- rows (y-clustered, tol=6) --")
ws = sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0]))
rows, cur, last = [], [], None
for w in ws:
    yc = (w[1] + w[3]) / 2
    if last is None or abs(yc - last) <= 6:
        cur.append(w); last = yc if last is None else last
    else:
        rows.append(cur); cur, last = [w], yc
if cur:
    rows.append(cur)
for r in rows[:16]:
    r.sort(key=lambda w: w[0])
    print("   ", " | ".join(w[4] for w in r)[:120])
doc.close()
