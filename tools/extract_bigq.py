# -*- coding: utf-8 -*-
"""Extract 综合题 (41-47) stems + 参考答案/解析 from the answer-key PDFs."""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyze as A  # noqa: E402
from syllabus import KP_BY_ID  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
ANS = os.path.join(ROOT, "work", "text_ans")
COMPOSITE_POINTS = {41: 13, 42: 10, 43: 13, 44: 10, 45: 8, 46: 7, 47: 9}

JUNK = re.compile(r"<<<PAGE \d+>>>|第\s*\d+\s*页\s*共\s*\d+\s*页|"
                  r"\d{4}\s*年[^\n]{0,20}第\s*\d+\s*页[^\n]*|【答案】|【解析】")


def paper_segments(year):
    """Full question text from the 试卷 itself."""
    src = A.find_text(year)
    if not src:
        return {}
    best = None
    for path, kind in src:
        body = A.strip_preamble(A.clean(open(path, encoding="utf-8").read()))
        segs = A.split_sequential(body)
        sc = (len(segs), sum(len(v) for v in segs.values()))
        if best is None or sc > best[0]:
            best = (sc, segs)
    return best[1] if best else {}


def solution_segments(year):
    """解析 text split by 41..47 anchors, taken from the 综合应用题 section.

    2019/2021/2023 的解析 PDF 是扫描件，文字层为空，改用 OCR 结果。
    """
    txt = ""
    for fn in (f"{year}.txt", f"{year}.ocr.txt"):
        p = os.path.join(ANS, fn)
        if not os.path.exists(p):
            continue
        cand = open(p, encoding="utf-8").read()
        if len(cand) > 2000:
            txt = cand
            break
    if not txt:
        return {}
    txt = re.sub(r"<<<PAGE \d+>>>", "\n", txt)
    start = txt.find("综合应用题")
    if start < 0:
        start = txt.find("41")
    if start < 0:
        return {}
    seg = txt[start:]

    def split_by(anchors, span):
        """anchors: [(pos, q)] sorted; slice each block to the next anchor."""
        got, startpos = {}, {}
        for i, (pos, q) in enumerate(anchors):
            if not (41 <= q <= 47) or q in got:
                continue
            end = anchors[i + 1][0] if i + 1 < len(anchors) else span
            got[q] = seg[pos:end]
            startpos[q] = pos
        # 短得像残片：多半是被下一个锚点（其实是正文里的数字）截断，向后补一段
        for q, body in list(got.items()):
            if len(body) < 80 and q in startpos:
                got[q] = seg[startpos[q]: startpos[q] + 900]
        return got

    out = {}
    strategies = [
        # 1) 行首题号 41..47
        [(m.start(), int(m.group(1)))
         for m in re.finditer(r"(?m)^\s*(\d{1,2})\s*[.．、•·)）]", seg)],
        # 2) 任意位置的 41..47；不能紧跟数字（否则 "41.25 GB/s" 会被当成第 41 题）
        [(m.start(), int(m.group(1)))
         for m in re.finditer(r"(?<![\d.])(4[1-7])\s*[.．、•·)）](?!\d)", seg)],
        # 3) "4.1." 这种写法（2025 年）
        sorted((m.start(), 40 + int(m.group(1)))
               for m in re.finditer(
                   r"(?<![\d.])4\s*[.．、]\s*([1-7])(?:\s*[.．、]|\s*【)(?!\d)", seg)),
    ]
    for anchors in strategies:
        for q, body in split_by(sorted(anchors), len(seg)).items():
            out.setdefault(q, body)

    # 41 题常紧跟在「综合应用题」标题后，可能没有独立题号行
    if 41 not in out:
        allpos = [p for anchors in strategies for p, _ in anchors if 41 <= _ <= 47]
        if allpos:
            out[41] = seg[:min(allpos)]
    return out


def tidy(s, limit):
    """保留换行与行首缩进（代码/表格需要），只压行内多余空格。"""
    s = JUNK.sub("\n", s)
    s = s.replace("\r", "").replace("\u3000", "  ")
    lines = []
    for ln in s.split("\n"):
        ln = ln.rstrip()
        m = re.match(r"^([ \t]*)(.*)$", ln)
        indent = m.group(1).replace("\t", "    ")
        rest = re.sub(r"[ \t]+", " ", m.group(2))
        lines.append(indent + rest)
    s = "\n".join(lines)
    s = re.sub(r"\n{3,}", "\n\n", s).strip(" \n")
    s = re.sub(r"^[:：]\s*", "", s)
    s = re.sub(r"^【?解析】?\s*[：:]?\s*", "", s)
    s = re.sub(r"^参考答案\s*[：:]?\s*", "", s)
    return s[:limit]


def main():
    qs = json.load(open(os.path.join(ROOT, "work", "out", "questions.json"),
                        encoding="utf-8"))
    fp = os.path.join(OUT, "data", "figures.json")
    figs = {}
    if os.path.exists(fp):
        raw = json.load(open(fp, encoding="utf-8"))
        figs = {k: (v if isinstance(v, dict) else {"p": v, "scan": False})
                for k, v in raw.items()}
    rows = []
    no_sol = []
    for year in sorted({q["year"] for q in qs}):
        stems = paper_segments(year)
        sols = solution_segments(year)
        for q in qs:
            if q["year"] != year or q["q"] < 41 or not q["kp"]:
                continue
            kp = KP_BY_ID[q["kp"]]
            stem = tidy(stems.get(q["q"], q["stem"]), 1400)
            sol = tidy(sols.get(q["q"], ""), 2400)
            if not sol:
                no_sol.append((year, q["q"]))
            row = {
                "y": year, "q": q["q"], "p": COMPOSITE_POINTS.get(q["q"], 8),
                "s": kp[1], "ch": kp[2], "kp": q["kp"], "kn": kp[4],
                "st": stem, "sol": sol,
            }
            fg = figs.get(f"{year}-{q['q']}")
            if fg:
                row["im"] = fg["p"]
                if fg.get("scan"):
                    row["imscan"] = 1
            rows.append(row)
    rows.sort(key=lambda r: (r["y"], r["q"]))
    dest = os.path.join(OUT, "data", "bigq.json")
    json.dump(rows, open(dest, "w", encoding="utf-8"), ensure_ascii=False,
              separators=(",", ":"))
    have = sum(1 for r in rows if r["sol"])
    print(f"综合题 {len(rows)} 道，其中有解析 {have} 道 -> {dest}")
    if no_sol:
        print(f"缺解析 {len(no_sol)} 道: {no_sol}")
    from collections import Counter
    print("按年份解析覆盖:", dict(sorted(Counter(
        r["y"] for r in rows if r["sol"]).items())))


if __name__ == "__main__":
    main()
