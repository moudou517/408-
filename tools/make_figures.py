# -*- coding: utf-8 -*-
"""Render all 408 figures from summary.json."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import viz  # noqa: E402
from syllabus import KP_BY_ID, SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
FIG = os.path.join(OUT, "fig")
os.makedirs(FIG, exist_ok=True)

S = json.load(open(os.path.join(OUT, "data", "summary.json"), encoding="utf-8"))

ORDER = ["DS", "CO", "OS", "NET"]


def figure_frequency():
    """分科题量 + 高频章节条形图。"""
    for s in ORDER:
        rows = [c for c in S["chapters"] if c["subject"] == s]
        rows.sort(key=lambda c: -c["points"])
        labels = [f'{c["chapter"]}' for c in rows]
        vals = [c["points"] for c in rows]
        viz.draw_bars(
            f'{SUBJECTS[s]}：各章历史累计分值（2009–2026）',
            labels, vals, os.path.join(FIG, f"03_章节分值_{s}.png"),
            figsize=(13, max(5, 0.55 * len(labels))), subject=s,
            xlabel="累计分值", color_map=None,
        )


def figure_kp_top():
    """每科 TOP 知识点。"""
    for s in ORDER:
        rows = [k for k in S["kps"] if k["subject"] == s][:16]
        if not rows:
            continue
        labels = [f'{k["name"]}' for k in rows]
        vals = [k["points"] for k in rows]
        viz.draw_bars(
            f'{SUBJECTS[s]}：高频知识点 TOP{len(rows)}（累计分值）',
            labels, vals, os.path.join(FIG, f"04_高频知识点_{s}.png"),
            figsize=(14, max(5, 0.5 * len(labels))), subject=s,
            xlabel="累计分值",
        )


def figure_chapter_year():
    """章节 × 年份 热力图（按科目）。"""
    years = S["years"]
    for s in ORDER:
        rows = [c["chapter"] for c in S["chapters"] if c["subject"] == s]
        if not rows:
            continue
        matrix = []
        for ch in rows:
            line = []
            for y in years:
                line.append(S["chapter_year"].get(f"{ch}|{y}", 0))
            matrix.append(line)
        viz.draw_matrix(
            f'{SUBJECTS[s]}：各章逐年出题数（{years[0]}–{years[-1]}）',
            rows, [str(y) for y in years], matrix,
            os.path.join(FIG, f"05_章节年份热力_{s}.png"),
            figsize=(max(12, 0.55 * len(years) + 6), max(6, 0.42 * len(rows) + 2.5)),
            xlabel="年份", ylabel="章节",
        )


def figure_subject_split():
    """四科累计分值（与大纲满分对照）。"""
    labels = [SUBJECTS[k] for k in ORDER]
    vals = [S["subjects"][k]["points"] for k in ORDER]
    viz.draw_bars(
        "四科累计分值（2009–2026 全部真题）",
        labels, vals, os.path.join(FIG, "02_分科分值.png"),
        figsize=(10, 5.2), subject="MIX", xlabel="累计分值", horizontal=True,
        color_map={SUBJECTS[k]: viz.PALETTE[k]["mid"] for k in ORDER},
    )


def main():
    figure_subject_split()
    figure_frequency()
    figure_kp_top()
    figure_chapter_year()
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
