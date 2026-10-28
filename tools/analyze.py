# -*- coding: utf-8 -*-
"""Parse every 408 paper into individual questions and classify each to a syllabus KP."""

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from syllabus import KPS, PAPER  # noqa: E402

ROOT = r"E:\CST\408"
TEXT = os.path.join(ROOT, "work", "text")
OUTDIR = os.path.join(ROOT, "work", "out")
os.makedirs(OUTDIR, exist_ok=True)

YEARS = list(range(2009, 2027))

INSTR = re.compile(
    r"(考生须知|答题前|考生编号|条形码|涂写|试题册|答题卡|草稿纸|黑色字迹|2B铅笔|"
    r"超出答题区域|非选择题的答案|选择题的答案必须)"
)


def subject_of(num):
    table = PAPER["选择"] if num <= 40 else PAPER["综合"]
    for subj, lo, hi in table:
        if lo <= num <= hi:
            return subj
    return None


def find_text(year):
    """Return (path, kind) for every usable extraction of `year`.

    rapidocr fixes reading order for the interleaved text layers, but it can also
    drop a low-confidence line; the PDF text layer sometimes keeps questions OCR
    loses. So we keep both and let main() pick whichever parses more questions.
    """
    cands = []
    for p in glob.glob(os.path.join(TEXT, "*.txt")):
        base = os.path.basename(p)
        m = re.search(r"(19|20)\d{2}", base)
        if not m or m.group(0) != str(year):
            continue
        body = open(p, encoding="utf-8").read()
        cjk = len(re.findall(r"[\u4e00-\u9fff]", body))
        if base.endswith(".ocr.txt"):
            if cjk > 800:
                cands.append((p, "ocr"))
        elif cjk > 1500:
            cands.append((p, "text"))
    return cands


def clean(body):
    body = re.sub(r"(?s)^#.*?\n\n", "", body)
    body = re.sub(r"<<<PAGE \d+>>>.*?(?=\n)", "\n", body)
    body = re.sub(r"<<<PAGE \d+>>>", "\n", body)
    body = re.sub(r"\d{4}\s*年?[^\n]{0,20}第\s*\d+\s*页[^\n]*共\s*\d+\s*页", "", body)
    body = re.sub(r"第\s*\d+\s*页\s*共\s*\d+\s*页", "", body)
    return body


def strip_preamble(body):
    """Drop the exam-instructions block and start at the first real question."""
    idx = -1
    for marker in ["单项选择题", "一、单选", "一．单选", "一.单选"]:
        j = body.find(marker)
        if j != -1 and (idx == -1 or j > idx):
            idx = j
    start = idx if idx != -1 else 0
    # drop instruction lines after the marker
    lines = body[start:].splitlines()
    keep = []
    for ln in lines:
        if INSTR.search(ln) and len(ln) < 120:
            continue
        keep.append(ln)
    return "\n".join(keep)


def num_pattern(n, strict):
    """Shells of the exam zero-pad single digits (`01．`), so allow an optional 0."""
    core = f"0?{n}" if n < 10 else str(n)
    if strict:
        return r"(?m)^[ \t]*" + core + r"[ \t]*[.．、)）][ \t]*"
    return r"(?<![\d.])" + core + r"\s*[.．、)）]\s*(?=[^\d])"


NUM_PAT = r"(?<![\d.])\b{n}\s*[.．、)）]\s*(?=[^\d])"   # kept for reference
NUM_STRICT = r"(?m)^[ \t]*{n}[ \t]*[.．、)）][ \t]*"


def section_bounds(body):
    """Return (choice_start, comp_start, end).

    The choice-section marker is only honoured when it appears near the top;
    otherwise the preamble strip already cleaned things and we scan from 0.
    """
    comp = -1
    for marker in ["综合应用题", "二、综合题"]:
        j = body.find(marker)
        if j != -1:
            comp = j
            break
    choice = 0
    for marker in ["单项选择题", "单项选择"]:
        j = body.find(marker, 0, 3000)
        if j != -1:
            choice = j
            break
    return choice, (comp if comp != -1 else len(body)), len(body)


def collect_anchors(body, start, end, lo, hi):
    """All plausible anchors for questions lo..hi, with a score for line-anchored ones."""
    out = []
    for n in range(lo, hi + 1):
        seen = []
        for strict, bonus in ((True, 3), (False, 1)):
            pat = num_pattern(n, strict)
            for m in re.finditer(pat, body[:end]):
                if m.start() < start:
                    continue
                if any(abs(m.start() - s) < 3 for s in seen):
                    continue
                seen.append(m.start())
                out.append((m.start(), m.end(), n, bonus))
    out.sort()
    return out


def best_chain(anchors):
    """Longest chain with strictly increasing question number (anchors are pos-sorted).

    Primary: cover as many distinct question numbers as possible.
    Secondary: prefer line-anchored (higher-scoring) anchors.
    """
    if not anchors:
        return []
    m = len(anchors)
    dp = [(1, anchors[i][3], -1) for i in range(m)]
    for i in range(m):
        ni = anchors[i][2]
        for j in range(i):
            if anchors[j][2] >= ni:
                continue
            cand = (dp[j][0] + 1, dp[j][1] + anchors[i][3], j)
            if cand[0] > dp[i][0] or (cand[0] == dp[i][0] and cand[1] > dp[i][1]):
                dp[i] = cand
    best_i = max(range(m), key=lambda k: (dp[k][0], dp[k][1]))
    chain = []
    i = best_i
    while i != -1:
        chain.append(anchors[i])
        i = dp[i][2]
    chain.reverse()
    return chain


def split_sequential(body):
    """Q1..Q40 from the choice section, Q41..Q47 from the comprehensive section.

    Scoped per section so sub-item numbering like (1)(2) inside a big question
    cannot hijack the global question index.
    """
    c0, c1, c2 = section_bounds(body)
    picked = {}
    for lo, hi, s, e in ((1, 40, c0, c1), (41, 47, c1, c2)):
        chain = best_chain(collect_anchors(body, s, e, lo, hi))
        for pos, _end, n, _bonus in chain:
            picked[n] = pos

    ordered = sorted(picked.items(), key=lambda kv: kv[1])
    segs = {}
    for i, (n, start) in enumerate(ordered):
        end = ordered[i + 1][1] if i + 1 < len(ordered) else len(body)
        seg = body[start:end].strip()
        seg = re.sub(r"(?m)^[ \t]*\d{1,2}[ \t]*[.．、)）][ \t]*", "", seg, count=1)
        segs[n] = seg
    return segs


def norm(s):
    s = re.sub(r"\s+", "", s)
    for a, b in [("（", "("), ("）", ")"), ("，", ","), ("：", ":"), ("；", ";")]:
        s = s.replace(a, b)
    return s


def split_stem_options(seg):
    """Separate the question stem from the four options (options pollute scoring)."""
    m = re.search(r"(?:^|\s)[AＡ]\s*[.．、]", seg)
    if m and m.start() > 10:
        return seg[: m.start()], seg[m.start():]
    return seg, ""


def score_kp(text, kp, mult=1.0):
    _id, _subj, _ch, _sec, _name, kws = kp
    t = norm(text)
    total = 0.0
    hits = []
    for kw in kws:
        k = norm(kw)
        if not k:
            continue
        c = t.count(k)
        if c == 0:
            continue
        w = 1.0 + 0.4 * len(k)
        total += mult * w * min(c, 3)
        hits.append(kw)
    return total, hits


def classify_any(seg):
    """Score every KP in every subject; return (subject, kp, alts, conf).

    Used for the comprehensive questions (41-47): those are NOT always laid out in
    subject order (e.g. 2014 puts OSPF at 42 and 生产者-消费者 at 47), so the subject
    must come from the content, not the question number.
    """
    stem, opts = split_stem_options(seg)
    scored = {}
    for kp in KPS:
        s1, _ = score_kp(stem, kp, 3.0)
        s2, _ = score_kp(opts, kp, 1.0)
        s = s1 + s2
        if s > 0:
            scored[kp[0]] = (s, kp)
    if not scored:
        return None, None, [], 0.0
    subj_best = {}
    for kid, (s, kp) in scored.items():
        cur = subj_best.get(kp[1])
        if cur is None or s > cur[0]:
            subj_best[kp[1]] = (s, kid)
    subj = max(subj_best, key=lambda k: subj_best[k][0])
    cands = sorted([(s, kp) for kid, (s, kp) in scored.items() if kp[1] == subj],
                   key=lambda x: -x[0])
    top = cands[0]
    second = cands[1][0] if len(cands) > 1 else 0.0
    conf = 1.0 if second == 0 else round(top[0] / (top[0] + second), 3)
    alts = [(c[1][0], round(c[0], 1)) for c in cands[:3]]
    return subj, top[1][0], alts, conf


def classify(seg, subj):
    stem, opts = split_stem_options(seg)
    cands = []
    for kp in KPS:
        if kp[1] != subj:
            continue
        s1, h1 = score_kp(stem, kp, 3.0)
        s2, h2 = score_kp(opts, kp, 1.0)
        s = s1 + s2
        if s > 0:
            cands.append((s, kp, h1 + h2))
    cands.sort(key=lambda x: -x[0])
    if not cands:
        return None, [], 0.0
    top = cands[0]
    second = cands[1][0] if len(cands) > 1 else 0.0
    conf = 1.0 if second == 0 else round(top[0] / (top[0] + second), 3)
    alts = [(c[1][0], round(c[0], 1)) for c in cands[:3]]
    return top[1][0], alts, conf


def main():
    # manual corrections: {"YYYY-Q": "KP.ID", ...}
    ov_path = os.path.join(ROOT, "work", "overrides.json")
    overrides = {}
    if os.path.exists(ov_path):
        overrides = json.load(open(ov_path, encoding="utf-8"))
        print(f"loaded {len(overrides)} manual overrides")

    rows = []
    for yr in YEARS:
        sources = find_text(yr)
        if not sources:
            print(f"{yr}: MISSING")
            continue
        # try every available extraction, keep the one that recovers the most questions
        best = None
        for path, kind in sources:
            body = strip_preamble(clean(open(path, encoding="utf-8").read()))
            qs = split_sequential(body)
            score = (len(qs), sum(len(v) for v in qs.values()))
            if best is None or score > best[0]:
                best = (score, kind, qs)
        _score, kind, qs = best
        got = sorted(qs)
        missing = [n for n in range(1, 48) if n not in qs]
        for num in got:
            if num <= 40:
                subj = subject_of(num)
                kp, alts, conf = classify(qs[num], subj)
            else:
                subj, kp, alts, conf = classify_any(qs[num])
            key = f"{yr}-{num}"
            if key in overrides:
                ov = overrides[key]
                if isinstance(ov, dict):
                    kp = ov.get("kp", kp)
                    subj = ov.get("subject") or (
                        next((k[1] for k in KPS if k[0] == kp), subj)
                    )
                else:
                    kp = ov
                    # a bare KP id also fixes the subject, so chapter/subject never disagree
                    subj = next((k[1] for k in KPS if k[0] == kp), subj)
                conf = 1.0
            rows.append(
                {
                    "year": yr,
                    "q": num,
                    "subject": subj,
                    "type": "选择" if num <= 40 else "综合",
                    "kp": kp,
                    "alt": alts,
                    "conf": conf,
                    "stem": re.sub(r"\s+", " ", qs[num])[:200],
                    "src": kind,
                }
            )
        print(f"{yr} [{kind}] got {len(got)}/47  missing={missing}")

    with open(os.path.join(OUTDIR, "questions.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    from collections import Counter

    print(f"\nTotal: {len(rows)}")
    low = [r for r in rows if r["conf"] < 0.55]
    unk = [r for r in rows if r["kp"] is None]
    print(f"low-conf {len(low)}, unclassified {len(unk)}")
    for r in unk[:25]:
        print(f"  UNK {r['year']} Q{r['q']} {r['subject']}: {r['stem'][:100]}")


if __name__ == "__main__":
    main()
