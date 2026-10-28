# -*- coding: utf-8 -*-
"""Spot-check bigq solution quality after the anchor fixes."""

import json

d = json.load(open(r"E:\CST\408\out\data\bigq.json", encoding="utf-8"))
for y, q in [(2010, 42), (2025, 41), (2022, 41), (2024, 41), (2018, 42)]:
    hit = [x for x in d if x["y"] == y and x["q"] == q]
    if not hit:
        print(f"{y}-{q}: 不存在")
        continue
    r = hit[0]
    sol = r.get("sol") or ""
    print(f"{y}-{q}: {len(sol)} 字, 换行 {sol.count(chr(10))}")
    print("   " + repr(sol[:110]))

print()
have = [r for r in d if r.get("sol")]
print("有解析:", len(have), "/", len(d))
print("平均长度:", round(sum(len(r["sol"]) for r in have) / max(len(have), 1)))
print("含换行:", sum(1 for r in have if "\n" in r["sol"]))
print("过短(<120 字):", sum(1 for r in have if len(r["sol"]) < 120))
