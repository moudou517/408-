# -*- coding: utf-8 -*-
"""Diagnose why some questions fail option parsing."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A  # noqa: E402
from build_quiz_data import split_options  # noqa: E402

ROOT = r"E:\CST\408"
WORK = os.path.join(ROOT, "work", "out")

qs = json.load(open(os.path.join(WORK, "questions.json"), encoding="utf-8"))
answers = json.load(open(os.path.join(ROOT, "work", "answers.json"), encoding="utf-8"))

full = {}
for yr in sorted({q["year"] for q in qs}):
    src = A.find_text(yr)
    if not src:
        continue
    best = None
    for path, kind in src:
        body = A.strip_preamble(A.clean(open(path, encoding="utf-8").read()))
        segs = A.split_sequential(body)
        sc = (len(segs), sum(len(v) for v in segs.values()))
        if best is None or sc > best[0]:
            best = (sc, segs)
    if best:
        for n, seg in best[1].items():
            full[(yr, n)] = seg

bad = []
for q in qs:
    if q["q"] > 40:
        continue
    key = (q["year"], q["q"])
    if not answers.get(str(q["year"]), {}).get(str(q["q"])):
        continue
    stem, opts = split_options(full.get(key, ""))
    if not stem:
        bad.append((q["year"], q["q"], full.get(key, "")))

print(f"bad-options: {len(bad)}\n")
for y, q, seg in bad[:14]:
    s = " ".join(seg.split())
    print(f"--- {y}-{q} ---")
    print("  ", s[:260])
