# -*- coding: utf-8 -*-
"""Diagnose and tune question splitting across all years."""

import glob
import os
import re
import sys

ROOT = r"E:\CST\408"
TEXT = os.path.join(ROOT, "work", "text")

INSTR = re.compile(
    r"(考生须知|答题前|考生编号|条形码|涂写|试题册|答题卡|草稿纸|黑色字迹|2B铅笔|"
    r"超出答题区域|非选择题的答案|选择题的答案必须|考试结束|按规定交回|认真填写|"
    r"页共|第\s*\d+\s*页)"
)

ANY_NUM = re.compile(r"(?<![\d.])(\d{1,2})\s*[.．、)）]")


def load(year):
    for p in glob.glob(os.path.join(TEXT, "*.txt")):
        b = os.path.basename(p)
        m = re.search(r"(19|20)\d{2}", b)
        if not m or m.group(0) != str(year):
            continue
        if b.endswith(".ocr.txt"):
            continue
        body = open(p, encoding="utf-8").read()
        if len(re.findall(r"[\u4e00-\u9fff]", body)) > 1500:
            return p, body
    for p in glob.glob(os.path.join(TEXT, "*.ocr.txt")):
        b = os.path.basename(p)
        m = re.search(r"(19|20)\d{2}", b)
        if m and m.group(0) == str(year):
            body = open(p, encoding="utf-8").read()
            if len(re.findall(r"[\u4e00-\u9fff]", body)) > 800:
                return p, body
    return None, None


def prep(body):
    body = re.sub(r"(?s)^#.*?\n\n", "", body)
    body = re.sub(r"<<<PAGE \d+>>>", "\n", body)
    return body


def start_offset(body):
    for marker in ["单项选择题", "一、单项选择", "一．单项选择", "一.单项选择"]:
        j = body.find(marker)
        if j != -1:
            return j
    return 0


def anchors(body, start):
    out = []
    for m in ANY_NUM.finditer(body, start):
        n = int(m.group(1))
        if 1 <= n <= 47:
            out.append((m.start(), m.end(), n))
    return out


def choose(body, start):
    """Greedy sequential selection with one-step skips."""
    cand = anchors(body, start)
    picked = {}
    expect = 1
    i = 0
    stale = 0
    while i < len(cand) and expect <= 47:
        pos, end, n = cand[i]
        if n == expect:
            picked[n] = (pos, end)
            expect += 1
            stale = 0
            i += 1
        elif n > expect and stale > 40:
            # give up on the missing number(s)
            expect += 1
            stale = 0
        else:
            stale += 1
            i += 1
    return picked, cand


def main():
    years = [int(x) for x in sys.argv[1:]] or list(range(2009, 2027))
    for yr in years:
        path, body = load(yr)
        if not path:
            print(f"{yr}: NO TEXT")
            continue
        body = prep(body)
        st = start_offset(body)
        picked, cand = choose(body, st)
        got = sorted(picked)
        missing = [n for n in range(1, 48) if n not in picked]
        tag = "OCR" if path.endswith(".ocr.txt") else "txt"
        print(f"{yr} [{tag}] anchors={len(cand)} picked={len(got)} missing={missing}")
        if len(got) < 44:
            # show where it stalled
            for n in range(1, 48):
                if n not in picked:
                    print(f"   first missing Q{n}; nearby anchors:", [c[2] for c in cand[:120]][:60])
                    break


if __name__ == "__main__":
    main()
