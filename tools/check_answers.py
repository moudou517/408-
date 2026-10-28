# -*- coding: utf-8 -*-
"""Check whether the source PDFs carry answer keys."""

import glob
import os
import re

PAT = re.compile(r"(参考答案|答案解析|答案与解析|【答案】|答案：|正确答案|思路分析|真题解析|历年真题解析)")
MARK = re.compile(r"(?:^|\n)\s*(?:答案|【答案】)\s*[:：]?\s*([A-D]{1,4})")

for p in sorted(glob.glob(r"E:\CST\408\work\text\*.txt")):
    b = open(p, encoding="utf-8").read()
    hits = {}
    for m in PAT.finditer(b):
        hits[m.group(1)] = hits.get(m.group(1), 0) + 1
    name = os.path.basename(p).replace(".ocr.txt", "").replace(".txt", "")
    print(f"{name[:24]:26s} len={len(b):6d}  hits={hits if hits else '-'}")
