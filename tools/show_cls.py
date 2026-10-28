# -*- coding: utf-8 -*-
"""Print the classification for selected years, for manual review."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syllabus import KP_BY_ID  # noqa: E402

P = r"E:\CST\408\work\out\questions.json"
rows = json.load(open(P, encoding="utf-8"))
years = [int(x) for x in sys.argv[1:]] or [2025]

for yr in years:
    sub = [r for r in rows if r["year"] == yr]
    if not sub:
        print(f"{yr}: no rows")
        continue
    print("=" * 110)
    print(f"{yr}  ({len(sub)} questions)")
    for r in sorted(sub, key=lambda x: x["q"]):
        kp = r["kp"] or "NONE"
        name = KP_BY_ID[kp][4][:20] if r["kp"] else "-"
        alt = ",".join(a[0] for a in r["alt"][1:3])
        print(f"  Q{r['q']:>2} [{kp:<8}] {name:<22} c={r['conf']:.2f} alt={alt:<18} | {r['stem'][:62]}")
