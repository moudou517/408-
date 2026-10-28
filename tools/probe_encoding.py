"""Probe garbled-font PDFs: are the extracted chars latin-1 carriers of GBK bytes?"""

import os
import re

import pymupdf

CASES = [
    r"E:\CST\408\2009-2025计算机408统考真题\2009年计算机408统考真题.pdf",
    r"E:\CST\408\2009-2025计算机408统考真题\2016年计算机408统考真题.pdf",
    r"E:\CST\408\2009-2025计算机408统考真题\2023年计算机408统考真题.pdf",
    r"E:\CST\408\2009-2025计算机408统考真题\2018年计算机408统考真题.pdf",
]


def try_decode(sample):
    out = []
    for enc_chain in (("latin-1", "gbk"), ("latin-1", "gb18030"), ("cp1252", "gbk"), ("latin-1", "big5")):
        try:
            b = sample.encode(enc_chain[0])
            txt = b.decode(enc_chain[1], "replace")
            cjk = len(re.findall(r"[\u4e00-\u9fff]", txt))
            out.append((enc_chain, cjk, txt[:120].replace("\n", " ")))
        except Exception as e:
            out.append((enc_chain, -1, f"{type(e).__name__}: {e}"))
    return out


for path in CASES:
    if not os.path.exists(path):
        print("missing", path)
        continue
    doc = pymupdf.open(path)
    print("=" * 100)
    print(os.path.basename(path), "pages", len(doc))
    # fonts on page 2
    pg = doc[1]
    fl = pg.get_fonts(full=True)
    print("  fonts:", [(f[3], f[2], f[1]) for f in fl][:6])
    raw = pg.get_text()
    print("  raw sample:", repr(raw[:100]))
    for chain, cjk, head in try_decode(raw):
        print(f"    {chain[0]:>8}->{chain[1]:<8} cjk={cjk:<5} {head}")
    doc.close()
