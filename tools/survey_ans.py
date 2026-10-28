# -*- coding: utf-8 -*-
"""Survey how each answer-key year encodes the correct option."""

import glob
import os
import re

PATTERNS = [
    ("参考答案X", re.compile(r"【参考答案】\s*([A-D])")),
    ("答案X", re.compile(r"【答案】\s*([A-D])")),
    ("答案:X", re.compile(r"答案\s*[:：]\s*([A-D])\b")),
    ("故本题选X", re.compile(r"故本题选\s*([A-D])")),
    ("故选X", re.compile(r"故选\s*([A-D])\b")),
    ("解析:", re.compile(r"解析\s*[:：]")),
    ("题号+解析", re.compile(r"(?m)^\s*(\d{1,2})\s*[.．、]\s*解析")),
]

files = sorted(glob.glob(r"E:\CST\408\work\text_ans\*.txt"))
print(f"{'year':<6}" + "".join(f"{n:>11}" for n, _ in PATTERNS))
for p in files:
    y = os.path.basename(p).replace(".txt", "")
    t = open(p, encoding="utf-8").read()
    if len(t) < 500:
        print(f"{y:<6}" + "   (image-only)" )
        continue
    row = []
    for _, rx in PATTERNS:
        row.append(str(len(rx.findall(t))))
    print(f"{y:<6}" + "".join(f"{v:>11}" for v in row))

print("\n--- 2009 前 1200 字符（看有没有答案速查表）---")
t = open(r"E:\CST\408\work\text_ans\2009.txt", encoding="utf-8").read()
print(re.sub(r"\n+", "\n", t[:1200]))
