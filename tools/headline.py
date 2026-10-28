# -*- coding: utf-8 -*-
"""Print headline numbers used in the final summary."""

import json

S = json.load(open(r"E:\CST\408\out\data\summary.json", encoding="utf-8"))
ny = len(S["years"])

print("TOP 12 全局（按年份覆盖降序，再看分值）:")
ks = sorted(S["kps"], key=lambda k: (-k["n_years"], -k["points"]))[:12]
for k in ks:
    print(f"  {k['id']:9s} {k['name'][:32]:34s} {k['n_years']:2d}/{ny}  {k['points']:3d}分  {k['chapter']}")

print("\n每科覆盖最高的知识点:")
for s in ["DS", "CO", "OS", "NET"]:
    r = [k for k in S["kps"] if k["subject"] == s]
    m = max(r, key=lambda k: (k["n_years"], k["points"]))
    n_bi = sum(1 for k in r if k["n_years"] >= 14)
    print(f"  {s}: 最稳 = {m['name'][:32]} ({m['n_years']}/{ny}); 该科“必考级”知识点数 = {n_bi}")

print("\n每科“必考”级知识点（≥14/18）:")
for s in ["DS", "CO", "OS", "NET"]:
    r = [k for k in S["kps"] if k["subject"] == s and k["n_years"] >= 14]
    r.sort(key=lambda k: -k["n_years"])
    print(f"  [{s}]")
    if not r:
        print("    （无 —— 该科考点分布较分散）")
    for k in r:
        print(f"    {k['name'][:34]:36s} {k['n_years']}/{ny}  {k['points']}分")

print("\n累计分值最高的 8 个知识点（含大题）:")
for k in sorted(S["kps"], key=lambda k: -k["points"])[:8]:
    print(f"  {k['name'][:34]:36s} {k['points']:3d}分  {k['count']:2d}题次")
