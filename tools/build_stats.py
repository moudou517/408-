# -*- coding: utf-8 -*-
"""Aggregate classified questions into statistics and render all figures."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from syllabus import KP_BY_ID, KPS, PAPER, SUBJECTS  # noqa: E402
import viz  # noqa: E402

ROOT = r"E:\CST\408"
WORK = os.path.join(ROOT, "work", "out")
OUT = os.path.join(ROOT, "out")
FIG = os.path.join(OUT, "fig")
os.makedirs(FIG, exist_ok=True)
os.makedirs(os.path.join(OUT, "data"), exist_ok=True)

# 各题型分值（按试卷结构：选择题2分；综合题分值随年份略异，取官方题干分值，
# 缺失时按 DS 23/CO 23/OS 15/NET 9 分摊）
COMPOSITE_POINTS = {
    41: 13, 42: 10, 43: 13, 44: 10, 45: 8, 46: 7, 47: 9,
}


def points_of(q):
    if q <= 40:
        return 2
    return COMPOSITE_POINTS.get(q, 2)


def main():
    rows = json.load(open(os.path.join(WORK, "questions.json"), encoding="utf-8"))
    # 只保留分类成功、且题目文本够长的记录
    keep = [r for r in rows if r["kp"] and len(r["stem"]) > 25]
    print(f"records {len(rows)} -> usable {len(keep)}")

    from collections import Counter, defaultdict

    # ---- 年份覆盖
    years = sorted({r["year"] for r in keep})
    per_year = Counter(r["year"] for r in keep)
    print("years:", years)
    print("per year:", dict(per_year))

    # ---- 科目汇总（题量 + 分值）
    subj_cnt = Counter()
    subj_pts = Counter()
    for r in keep:
        subj_cnt[r["subject"]] += 1
        subj_pts[r["subject"]] += points_of(r["q"])

    # ---- 章节汇总
    chap_cnt = Counter()
    chap_pts = Counter()
    for r in keep:
        ch = KP_BY_ID[r["kp"]][2]
        chap_cnt[(r["subject"], ch)] += 1
        chap_pts[(r["subject"], ch)] += points_of(r["q"])

    # ---- 知识点汇总
    kp_cnt = Counter()
    kp_pts = Counter()
    kp_years = defaultdict(set)
    for r in keep:
        kp_cnt[r["kp"]] += 1
        kp_pts[r["kp"]] += points_of(r["q"])
        kp_years[r["kp"]].add(r["year"])

    # ---- 年份×科目 矩阵
    ysub = defaultdict(int)
    for r in keep:
        ysub[(r["year"], r["subject"])] += 1

    # ---- 章节×年份 矩阵（按科目）
    ch_year = defaultdict(int)
    for r in keep:
        ch_year[(KP_BY_ID[r["kp"]][2], r["year"])] += 1

    summary = {
        "n_questions": len(keep),
        "years": years,
        "per_year": dict(per_year),
        "subjects": {
            s: {"count": subj_cnt[s], "points": subj_pts[s]} for s in SUBJECTS
        },
        "chapters": [
            {
                "subject": s,
                "chapter": ch,
                "count": chap_cnt[(s, ch)],
                "points": chap_pts[(s, ch)],
            }
            for (s, ch) in sorted(chap_cnt, key=lambda k: (-chap_pts[k], k))
        ],
        "kps": [
            {
                "id": k,
                "subject": KP_BY_ID[k][1],
                "chapter": KP_BY_ID[k][2],
                "section": KP_BY_ID[k][3],
                "name": KP_BY_ID[k][4],
                "count": kp_cnt[k],
                "points": kp_pts[k],
                "years": sorted(kp_years[k]),
                "n_years": len(kp_years[k]),
            }
            for k in sorted(kp_cnt, key=lambda k: (-kp_pts[k], -len(kp_years[k]), k))
        ],
        "year_subject": {f"{y}|{s}": ysub[(y, s)] for y in years for s in SUBJECTS},
        "chapter_year": {f"{c}|{y}": ch_year[(c, y)] for (c, y) in ch_year},
    }
    json.dump(summary, open(os.path.join(OUT, "data", "summary.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- 明细 CSV
    with open(os.path.join(OUT, "data", "questions_classified.csv"), "w",
              encoding="utf-8-sig") as f:
        f.write("年份,题号,题型,科目,章,节,知识点,分值,来源,题干摘录\n")
        for r in sorted(keep, key=lambda x: (x["year"], x["q"])):
            k = KP_BY_ID[r["kp"]]
            stem = r["stem"].replace('"', "'").replace(",", "，")[:120]
            f.write(f'{r["year"]},{r["q"]},{r["type"]},{SUBJECTS[k[1]]},'
                    f'{k[2]},{k[3]},{k[4]},{points_of(r["q"])},{r["src"]},"{stem}"\n')

    print("wrote summary.json + questions_classified.csv")
    return summary


if __name__ == "__main__":
    main()
