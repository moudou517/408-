# -*- coding: utf-8 -*-
"""Build the quiz dataset: full stem + 4 options + correct answer per MCQ.

Answers come from work/answers.json (parsed from the 解析 PDFs).
Only questions whose four options parse cleanly are included, so the quiz never
shows a malformed question.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from syllabus import KP_BY_ID  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
WORK = os.path.join(ROOT, "work", "out")

OPT = re.compile(r"(?<![A-Za-z0-9])([A-Da-d])\s*[.．、]\s*")
LEAD = re.compile(r"(?m)^\s*\d{1,2}\s*[.．、]\s*")
TAIL = re.compile(r"(?:\d{4}\s*年.{0,24}第\s*\d+\s*页.*?共\s*\d+\s*页|"
                  r"第\s*\d+\s*页\s*共\s*\d+\s*页|<<<PAGE \d+>>>|【答案】.*$|【解析】.*$)")


def clean(s):
    s = TAIL.sub(" ", s)
    s = LEAD.sub("", s)
    s = re.sub(r"[\u200b\ufeff]", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


def split_options(seg):
    """Return (stem, [A,B,C,D]) or (None, None).

    The PDF text layer interleaves two-column option blocks, so labels routinely
    arrive as A,C,B,D. Slice each option as "text between this label and the next
    label" — that keeps every label bound to its own text — then sort by label.
    """
    s = clean(seg)
    marks = [m for m in OPT.finditer(s)]
    if len(marks) < 4:
        return None, None

    picked = {}
    for i, m in enumerate(marks):
        ch = m.group(1).upper()
        if ch in picked:          # keep the first occurrence of each label
            continue
        end = marks[i + 1].start() if i + 1 < len(marks) else len(s)
        body = re.sub(r"\s+", " ", s[m.end():end]).strip(" 。；;，,")
        picked[ch] = (m.start(), body)

    if set(picked) != set("ABCD"):
        return None, None
    order = sorted(picked.values(), key=lambda t: t[0])
    stem = s[: order[0][0]].strip()
    if len(stem) < 8:
        return None, None
    opts = [picked[c][1] for c in "ABCD"]
    if any(len(o) < 1 or len(o) > 260 for o in opts):
        return None, None
    # 全部为空 = 图形类选项（如"A. B. C. D."配图），无法文字化
    if sum(len(o) for o in opts) == 0:
        return None, None
    return stem, opts


def load_explanations():
    """Per-question 解析 excerpt from the answer-key PDFs' text.

    Two layouts: inline years put the explanation right after 【答案】,
    older years use an "N. 解析：" heading.
    """
    import glob

    ex = {}
    for p in glob.glob(os.path.join(ROOT, "work", "text_ans", "*.txt")):
        base = os.path.basename(p)
        m = re.match(r"((?:19|20)\d{2})\.txt$", base)
        if not m:
            continue
        year = int(m.group(1))
        txt = open(p, encoding="utf-8").read()
        if len(txt) < 2000:
            continue
        txt = re.sub(r"<<<PAGE \d+>>>", "\n", txt)

        anchors = [(mm.start(), int(mm.group(1)))
                   for mm in re.finditer(r"(?m)^\s*(\d{1,2})\s*[.．、]", txt)]

        def seg_for(q, start):
            nxt = len(txt)
            for apos, aq in anchors:
                if apos > start:
                    nxt = apos
                    break
            return txt[start:nxt]

        if re.search(r"【(?:参考)?答案】", txt):
            # inline: explanation follows the answer marker
            for mm in re.finditer(r"【(?:参考)?答案】\s*[A-D][.．、]?", txt):
                prev = None
                for apos, aq in anchors:
                    if apos >= mm.start():
                        break
                    prev = aq
                if prev is None or not (1 <= prev <= 40) or (year, prev) in ex:
                    continue
                body = seg_for(prev, mm.end())
                ex[(year, prev)] = body
        else:
            for mm in re.finditer(r"(?m)^\s*(\d{1,2})\s*[.．、]\s*解析", txt):
                q = int(mm.group(1))
                if not (1 <= q <= 40) or (year, q) in ex:
                    continue
                ex[(year, q)] = seg_for(q, mm.end())

    out = {}
    for k, v in ex.items():
        v = v.replace("\r", "").replace("\t", "    ")
        v = re.sub(r"[ ]{2,}", " ", v)
        v = re.sub(r"\n{3,}", "\n\n", v)
        v = re.sub(r"^(?:[\s：:，,、.．])+", "", v)
        v = re.sub(r"^(?:【解析】|解析\s*[：:]?)", "", v).strip()
        v = re.sub(r"\[[^\]]*图[^\]]*\]", "", v)
        if len(v) >= 20:
            out[f"{k[0]}-{k[1]}"] = v[:320]
    return out


def load_figures():
    """{'YYYY-Q': {'p': 相对路径, 'scan': 是否原卷切片}}"""
    p = os.path.join(OUT, "data", "figures.json")
    if not os.path.exists(p):
        return {}
    raw = json.load(open(p, encoding="utf-8"))
    return {k: (v if isinstance(v, dict) else {"p": v, "scan": False})
            for k, v in raw.items()}


def main():
    qs = json.load(open(os.path.join(WORK, "questions.json"), encoding="utf-8"))
    answers = json.load(open(os.path.join(ROOT, "work", "answers.json"), encoding="utf-8"))
    expl = load_explanations()
    figs = load_figures()
    print(f"解析片段: {len(expl)} 条 · 插图: {len(figs)} 张")

    # 需要完整题干：analyze.py 只存了 200 字，这里重新切一次原文
    sys.argv = ["x"]
    import analyze as A

    full = {}
    for yr in sorted({q["year"] for q in qs}):
        sources = A.find_text(yr)
        if not sources:
            continue
        best = None
        for path, kind in sources:
            body = A.strip_preamble(A.clean(open(path, encoding="utf-8").read()))
            segs = A.split_sequential(body)
            score = (len(segs), sum(len(v) for v in segs.values()))
            if best is None or score > best[0]:
                best = (score, segs)
        if best:
            for n, seg in best[1].items():
                full[(yr, n)] = seg

    rows, skipped = [], []
    for q in qs:
        if q["q"] > 40:              # 综合题无单选答案，刷题器不收录
            continue
        key = (q["year"], q["q"])
        seg = full.get(key)
        ans = answers.get(str(q["year"]), {}).get(str(q["q"]))
        if not seg or not ans:
            skipped.append((q["year"], q["q"], "no-seg" if not seg else "no-ans"))
            continue
        stem, opts = split_options(seg)
        if not stem:
            skipped.append((q["year"], q["q"], "bad-options"))
            continue
        kp = KP_BY_ID.get(q["kp"])
        row = {
            "y": q["year"], "q": q["q"], "a": ans,
            "s": kp[1] if kp else q["subject"],
            "ch": kp[2] if kp else "",
            "kp": q["kp"], "kn": kp[4] if kp else "",
            "st": stem, "op": opts,
        }
        ex = expl.get(f'{q["year"]}-{q["q"]}')
        if ex:
            row["ex"] = ex
        fg = figs.get(f'{q["year"]}-{q["q"]}')
        if fg:
            row["im"] = fg["p"]
            if fg.get("scan"):
                row["imscan"] = 1
        rows.append(row)

    dest = os.path.join(OUT, "data", "quiz.json")
    json.dump(rows, open(dest, "w", encoding="utf-8"), ensure_ascii=False,
              separators=(",", ":"))
    n_all = sum(1 for q in qs if q["q"] <= 40)
    print(f"选择题总数 {n_all}  可刷 {len(rows)}  ({len(rows)/max(n_all,1)*100:.1f}%)")
    from collections import Counter
    why = Counter(s[2] for s in skipped)
    print("skipped reasons:", dict(why))
    by_year = Counter(r["y"] for r in rows)
    print("per year:", dict(sorted(by_year.items())))
    yrs_no_ans = sorted({q["year"] for q in qs if q["q"] <= 40} -
                        {int(y) for y in answers})
    if yrs_no_ans:
        print("years without answers:", yrs_no_ans)
    print("wrote", dest, f"{os.path.getsize(dest)/1024:.0f} KB")


if __name__ == "__main__":
    main()
