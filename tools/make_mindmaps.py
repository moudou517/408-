# -*- coding: utf-8 -*-
"""Build the five mind maps (overview + one per subject) from syllabus + measured weights."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import viz  # noqa: E402
from syllabus import KPS, SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
FIG = os.path.join(OUT, "fig")
os.makedirs(FIG, exist_ok=True)

S = json.load(open(os.path.join(OUT, "data", "summary.json"), encoding="utf-8"))
NY = max(len(S["years"]), 1)

# 年均分值（按章 / 按知识点）
chap_pts = {}
for c in S["chapters"]:
    chap_pts[(c["subject"], c["chapter"])] = c["points"]
kp_pts = {k["id"]: k["points"] for k in S["kps"]}
kp_years = {k["id"]: k["n_years"] for k in S["kps"]}

CHAPTER_ORDER = {
    "DS": ["绪论", "线性表", "栈、队列和数组", "串", "树与二叉树", "图", "查找", "排序"],
    "CO": ["计算机系统概述", "数据的表示和运算", "存储器层次结构", "指令系统",
           "中央处理器", "总线与输入输出"],
    "OS": ["操作系统概述", "进程管理", "内存管理", "文件管理", "输入输出管理"],
    "NET": ["计算机网络概述", "物理层", "数据链路层", "网络层", "传输层", "应用层"],
}

CHAPTER_TITLE = {
    "绪论": "第一章 绪论",
    "线性表": "第二章 线性表",
    "栈、队列和数组": "第三章 栈、队列和数组",
    "串": "第四章 串",
    "树与二叉树": "第五章 树与二叉树",
    "图": "第六章 图",
    "查找": "第七章 查找",
    "排序": "第八章 排序",
    "计算机系统概述": "第一章 系统概述",
    "数据的表示和运算": "第二章 数据表示与运算",
    "存储器层次结构": "第三章 存储器层次结构",
    "指令系统": "第四章 指令系统",
    "中央处理器": "第五章 中央处理器",
    "总线与输入输出": "第六章 总线与I/O",
    "操作系统概述": "第一章 概述",
    "进程管理": "第二章 进程管理",
    "内存管理": "第三章 内存管理",
    "文件管理": "第四章 文件管理",
    "输入输出管理": "第五章 I/O 管理",
    "计算机网络概述": "第一章 网络概述",
    "物理层": "第二章 物理层",
    "数据链路层": "第三章 数据链路层",
    "网络层": "第四章 网络层",
    "传输层": "第五章 传输层",
    "应用层": "第六章 应用层",
}


def mark(kp_id):
    """把实测热度写进叶子文本：用纯中文字符，避免 emoji 缺字变成方块。"""
    y = kp_years.get(kp_id, 0)
    if y >= 0.78 * NY:
        return "【必】"
    if y >= 0.55 * NY:
        return "【高】"
    return ""


def subject_mindmap(subj):
    branches = []
    for ch in CHAPTER_ORDER[subj]:
        leaves = [(k[4], k[0]) for k in KPS if k[1] == subj and k[2] == ch]
        if not leaves:
            continue
        leaves.sort(key=lambda t: -kp_pts.get(t[1], 0))
        txt = [f"{mark(kid)}{name}" for name, kid in leaves]
        pts = chap_pts.get((subj, ch), 0)
        share = f"年均 {pts/NY:.1f} 分"
        branches.append((CHAPTER_TITLE.get(ch, ch), txt, share))
    dest = os.path.join(FIG, f"01_思维导图_{subj}.png")
    viz.draw_mindmap(
        f"{SUBJECTS[subj]} · 考纲知识树（2009–2026 真题热度标注）",
        SUBJECTS[subj], branches, dest, subject=subj,
        note="【必】= 18 年中 14 年以上考到（必考）   【高】= 10–13 年考到（高频）",
    )
    return dest


def overview_mindmap():
    branches = []
    for subj in ["DS", "CO", "OS", "NET"]:
        leaves = []
        for ch in CHAPTER_ORDER[subj]:
            pts = chap_pts.get((subj, ch), 0)
            if pts == 0 and not any(k[1] == subj and k[2] == ch for k in KPS):
                continue
            leaves.append(f"{CHAPTER_TITLE.get(ch, ch)}  ·  年均 {pts/NY:.1f} 分")
        total = S["subjects"][subj]["points"]
        branches.append((f"{SUBJECTS[subj]}", leaves, f"累计 {total} 分 / 年均 {total/NY:.0f} 分"))
    dest = os.path.join(FIG, "00_总览知识地图.png")
    viz.draw_mindmap(
        "408 四科知识地图总览（分值 = 2009–2026 真题实测）",
        "408\n150 分", branches, dest, subject="MIX",
        note="选择题号即科目：1–11 数据结构 | 12–22 计组 | 23–32 操作系统 | 33–40 计算机网络",
    )
    return dest


if __name__ == "__main__":
    print(overview_mindmap())
    for s in ["DS", "CO", "OS", "NET"]:
        print(subject_mindmap(s))

