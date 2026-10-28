# -*- coding: utf-8 -*-
"""Recover the 40 multiple-choice answers per year.

Three paper layouts exist:
  A) 2009–2018 / 2020 / 2022 : "参考答案" table on page 1 (numbers + letters in a grid)
  B) 2024                     : "【参考答案】D" inline in the explanation
  C) 2025 / 2026              : "【答案】X" inline
  D) 2019 / 2021 / 2023       : image-only PDFs -> must OCR

For (A) the text layer interleaves the grid, so rebuild rows from word coordinates.
"""

import glob
import os
import re
import sys

import pymupdf

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "work", "text_ans")
os.makedirs(OUT, exist_ok=True)
LETTERS = "ABCD"


def pdf_of(year):
    for p in glob.glob(os.path.join(ROOT, "*真题解析.pdf")):
        m = re.search(r"(19|20)\d{2}", os.path.basename(p))
        if m and m.group(0) == str(year):
            return p
    return None


def rows_from_page(page, ytol=4.0):
    """Cluster words into visual rows, then order each row by x."""
    words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,word_no
    if not words:
        return []
    words = sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    rows, cur, last_y = [], [], None
    for w in words:
        yc = (w[1] + w[3]) / 2
        if last_y is None or abs(yc - last_y) <= ytol:
            cur.append(w)
            last_y = yc if last_y is None else last_y
        else:
            rows.append(cur)
            cur, last_y = [w], yc
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        r.sort(key=lambda w: w[0])
        out.append([w[4] for w in r])
    return out


def parse_grid(rows, want=40):
    """From visual rows like ['1.','B','9.','A',...] recover {qno: letter}."""
    ans = {}
    for toks in rows:
        # normalise: split tokens that glue number+letter like "1.B" or "B1."
        flat = []
        for t in toks:
            flat.extend(re.findall(r"\d{1,2}|[A-D]", t))
        # walk pairs (num, letter)
        i = 0
        while i < len(flat) - 1:
            a, b = flat[i], flat[i + 1]
            if a.isdigit() and b in LETTERS:
                q = int(a)
                if 1 <= q <= want and q not in ans:
                    ans[q] = b
                i += 2
            elif a in LETTERS and b.isdigit():
                q = int(b)
                if 1 <= q <= want and q not in ans:
                    ans[q] = a
                i += 2
            else:
                i += 1
    return ans


def grid_by_columns(page, want=40):
    """Fallback: numbers and letters may be in separate blocks (two-line cells).

    Reconstruct by matching each number's (x, y) with the nearest letter below it.
    """
    words = page.get_text("words")
    nums, lets = [], []
    for w in words:
        t = w[4].strip()
        if re.fullmatch(r"\d{1,2}[.．、]?", t):
            q = int(re.sub(r"\D", "", t))
            if 1 <= q <= want:
                nums.append((q, (w[0] + w[2]) / 2, (w[1] + w[3]) / 2))
        elif re.fullmatch(r"[A-D]", t):
            lets.append((t, (w[0] + w[2]) / 2, (w[1] + w[3]) / 2))
    ans = {}
    used = set()
    for q, x, y in sorted(nums, key=lambda n: n[1]):
        best, bd = None, 1e9
        for i, (ch, lx, ly) in enumerate(lets):
            if i in used:
                continue
            dx, dy = abs(lx - x), ly - y
            if dy < -2 or dy > 26:      # letter must sit just below the number
                continue
            d = dx * 2 + abs(dy - 12)
            if d < bd:
                bd, best = d, i
        if best is not None and bd < 40:
            ans[q] = lets[best][0]
            used.add(best)
    return ans


def inline_answers(txt):
    """'【参考答案】D' / '【答案】D' style.

    Each answer belongs to the question printed *above* it, so attach every marker
    to the nearest preceding question anchor.  Some years repeat markers, so
    indexing by ordinal would drift — backward search does not.
    """
    anchors = [(m.start(), int(m.group(1)))
               for m in re.finditer(r"(?m)^\s*(\d{1,2})\s*[.．、]", txt)]
    if not anchors:
        return {}
    out = {}
    pat = re.compile(r"【(?:参考)?答案】\s*([A-D])")
    for m in pat.finditer(txt):
        pos, letter = m.start(), m.group(1)
        prev = None
        for apos, q in anchors:
            if apos >= pos:
                break
            prev = q
        if prev is None or not (1 <= prev <= 40):
            continue
        out.setdefault(prev, letter)
    return out if len(out) >= 30 else {}


def parse_year(year):
    p = pdf_of(year)
    if not p:
        return None, "no pdf"
    doc = pymupdf.open(p)
    txt_all = "".join(pg.get_text("text") for pg in doc)

    # C) inline style first (unambiguous)
    inl = inline_answers(txt_all)
    if len(inl) >= 35:
        doc.close()
        return inl, "inline"

    # A) rebuild the page-1 grid
    for pi in range(min(3, len(doc))):
        page = doc[pi]
        rows = rows_from_page(page)
        ans = parse_grid(rows)
        if len(ans) >= 35:
            doc.close()
            return ans, f"grid(rows,p{pi+1})"
    for pi in range(min(3, len(doc))):
        ans = grid_by_columns(doc[pi])
        if len(ans) >= 35:
            doc.close()
            return ans, f"grid(cols,p{pi+1})"
    doc.close()
    return None, "unparsed"


def main():
    years = [int(x) for x in sys.argv[1:]] or list(range(2009, 2027))
    result = {}
    print(f"{'year':<6}{'n':>4}  {'method':<18} preview")
    for y in years:
        ans, how = parse_year(y)
        if ans:
            result[y] = {str(k): v for k, v in sorted(ans.items())}
            prev = "".join(result[y].get(str(i), "-") for i in range(1, 21))
            print(f"{y:<6}{len(ans):>4}  {how:<18} {prev}...")
        else:
            print(f"{y:<6}{0:>4}  {how:<18} -")
    import json
    dest = os.path.join(ROOT, "work", "answers.json")
    json.dump(result, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"\nwrote {dest}  years={len(result)}  total={sum(len(v) for v in result.values())}")


if __name__ == "__main__":
    main()
