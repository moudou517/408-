# -*- coding: utf-8 -*-
"""Verify the answer/explanation coverage embedded in browse.html."""

import json
import re

h = open(r"E:\CST\408\out\browse.html", encoding="utf-8").read()
m = re.search(r'<script id="payload" type="application/json">(.*?)</script>', h, re.S)
rows = json.loads(m.group(1))["rows"]

big = [r for r in rows if r["t"] == 1]
sel = [r for r in rows if r["t"] == 0]

print("rows", len(rows))
print("  有解析 x:", sum(1 for r in rows if r.get("x")))
print("  有答案 a:", sum(1 for r in rows if r.get("a")))
print("  有选项 o:", sum(1 for r in rows if r.get("o")))
print()
print(f"综合题 {len(big)}：有解析 {sum(1 for r in big if r.get('x'))}"
      f" / 有完整题干 {sum(1 for r in big if r.get('fs'))}")
print(f"选择题 {len(sel)}：有答案 {sum(1 for r in sel if r.get('a'))}"
      f" / 有选项 {sum(1 for r in sel if r.get('o'))}"
      f" / 有解析 {sum(1 for r in sel if r.get('x'))}")
print()

for r in big:
    if r.get("x"):
        print("综合题样例:", r["y"], r["q"], "| 解析", len(r["x"]), "字")
        print("   ", r["x"][:120].replace("\n", " "))
        break
for r in sel:
    if r.get("x") and r.get("o"):
        print("选择题样例:", r["y"], r["q"], "| 答案", r["a"], "| 选项", len(r["o"]),
              "| 解析", len(r["x"]), "字")
        print("   ", r["o"])
        print("   ", r["x"][:100].replace("\n", " "))
        break

nocover = [r for r in rows if not r.get("x") and not r.get("o")]
print()
print("完全没有解析/选项的题:", len(nocover))
