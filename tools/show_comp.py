# -*- coding: utf-8 -*-
"""Print the classifications of the comprehensive questions (41-47) for review."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syllabus import KP_BY_ID  # noqa: E402

rows = json.load(open(r"E:\CST\408\work\out\questions.json", encoding="utf-8"))
comp = [r for r in rows if r["q"] >= 41]
years = sorted({r["year"] for r in comp})

for y in years:
    print("=" * 108)
    qs = sorted([r for r in comp if r["year"] == y], key=lambda x: x["q"])
    for r in qs:
        kp = r["kp"] or "NONE"
        nm = KP_BY_ID[kp][4][:26] if r["kp"] else "-"
        print(f"{y} Q{r['q']} [{kp:<8}] {nm:<28} c={r['conf']:.2f} | {r['stem'][:66]}")
