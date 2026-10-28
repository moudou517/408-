# -*- coding: utf-8 -*-
"""Extract the answer-key (解析) PDFs into work/text_ans/ and report quality."""

import glob
import os
import re

import pymupdf

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "work", "text_ans")
os.makedirs(OUT, exist_ok=True)

pdfs = sorted(glob.glob(os.path.join(ROOT, "*真题解析.pdf")))
print(f"{len(pdfs)} 解析 PDF\n")

rows = []
for p in pdfs:
    base = os.path.basename(p)
    m = re.search(r"(19|20)\d{2}", base)
    year = m.group(0) if m else "?"
    dest = os.path.join(OUT, f"{year}.txt")
    try:
        doc = pymupdf.open(p)
        parts = []
        for i, page in enumerate(doc):
            parts.append(f"\n<<<PAGE {i+1}>>>\n" + page.get_text("text"))
        txt = "".join(parts)
        n = len(doc)
        doc.close()
        with open(dest, "w", encoding="utf-8") as f:
            f.write(f"# source: {p}\n# pages: {n}\n" + txt)
        cjk = len(re.findall(r"[\u4e00-\u9fff]", txt))
        # 有没有「答案 A」这类标记
        amarks = len(re.findall(r"(?:【答案】|答案\s*[:：]|正确答案)", txt))
        rows.append((year, base, n, len(txt), cjk, cjk / max(n, 1), amarks))
    except Exception as e:
        rows.append((year, base, -1, 0, 0, 0, 0))
        print(f"FAIL {base}: {type(e).__name__}: {e}")

print(f"{'year':<6}{'pages':>6}{'chars':>8}{'cjk':>7}{'cjk/pg':>8}{'ansmark':>9}  file")
for year, base, n, ln, cjk, pp, am in sorted(rows):
    flag = "" if pp > 120 else "   <-- 可能是扫描件/乱码"
    print(f"{year:<6}{n:>6}{ln:>8}{cjk:>7}{pp:>8.0f}{am:>9}  {base[:34]}{flag}")
