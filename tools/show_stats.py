# -*- coding: utf-8 -*-
"""Print the chapter / subject distribution for sanity checking."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syllabus import SUBJECTS  # noqa: E402

S = json.load(open(r"E:\CST\408\out\data\summary.json", encoding="utf-8"))
ny = len(S["years"])

print(f"years={ny}  n_questions={S['n_questions']}\n")
print("科目：")
for k in ["DS", "CO", "OS", "NET"]:
    d = S["subjects"][k]
    print(f"  {SUBJECTS[k]:12s} 题量 {d['count']:4d}  累计 {d['points']:4d}  年均 {d['points']/ny:5.1f}")

print("\n章节（按累计分值）：")
for c in S["chapters"]:
    print(f"  {SUBJECTS[c['subject']]:12s} {c['chapter']:16s} 题量 {c['count']:3d}  "
          f"累计 {c['points']:3d}  年均 {c['points']/ny:4.1f}")

print("\nTOP 25 知识点：")
for k in S["kps"][:25]:
    print(f"  {k['id']:10s} {k['name'][:34]:36s} 分值 {k['points']:3d}  "
          f"题次 {k['count']:2d}  覆盖 {k['n_years']:2d}/{ny}")
