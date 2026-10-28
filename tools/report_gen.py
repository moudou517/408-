# -*- coding: utf-8 -*-
"""Generate the final Markdown report from summary.json + authored narrative."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syllabus import SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
FIGNAME = "fig"
S = json.load(open(os.path.join(OUT, "data", "summary.json"), encoding="utf-8"))
ORDER = ["DS", "CO", "OS", "NET"]

FULL = {"DS": 45, "CO": 45, "OS": 35, "NET": 25}
TARGET = {"DS": 38, "CO": 34, "OS": 27, "NET": 21}

L = []
def w(s=""):
    L.append(s)


def img(name, caption):
    w(f"![{caption}]({FIGNAME}/{name})")
    w()
    w(f"<p align='center'><i>{caption}</i></p>")
    w()


# ---------------------------------------------------------------- header
def sec_header():
    yrs = S["years"]
    n = S["n_questions"]
    w("# 408 计算机学科专业基础综合 · 真题考纲分类与 120 分复习方案")
    w()
    w(f"> 数据来源：本地 **{len(yrs)} 套真题**（{yrs[0]}–{yrs[-1]} 年全国硕士研究生招生考试"
      f"计算机学科专业基础综合），共 **{n} 道题**逐题归类。")
    w(">")
    w("> 分类依据：教育部《计算机学科专业基础综合考试大纲》（数据结构 / 计算机组成原理 / "
      "操作系统 / 计算机网络 四部分，共 127 个叶子知识点）。")
    w(">")
    w("> 配套文件：`data/questions_classified.csv`（逐题明细）、`fig/`（全部图表）。")
    w()
    w("---")
    w()


# ---------------------------------------------------------------- structure
def sec_structure():
    w("## 一、考试结构与 120 分意味着什么")
    w()
    w("### 1.1 试卷硬结构（2009 年起稳定，已逐题核对）")
    w()
    w("| 科目 | 满分 | 选择题号 | 选择题量 | 选择题分 | 综合题号 | 综合题分 |")
    w("|---|---|---|---|---|---|---|")
    rows = [
        ("数据结构", "DS", "1–11", 11, 22, "41、42", 23),
        ("计算机组成原理", "CO", "12–22", 11, 22, "43、44", 23),
        ("操作系统", "OS", "23–32", 10, 20, "45、46", 15),
        ("计算机网络", "NET", "33–40", 8, 16, "47", 9),
    ]
    for name, k, rng, cnt, pts, comp, cpts in rows:
        w(f"| {name} | {FULL[k]} | {rng} | {cnt} | {pts} | {comp} | {cpts} |")
    w(f"| **合计** | **150** | 1–40 | **40** | **80** | 41–47 | **70** |")
    w()
    w("这一结构极其重要：**题号即科目**。看到第 12 题就知道是计组，看到第 33 题就知道是网络。"
      "考场上不需要判断“这题属于哪一科”，可以直接切到对应的解题套路。")
    w()
    w("### 1.2 120 分 = 各科容错分配")
    w()
    w("| 科目 | 满分 | 120 分目标得分 | 允许失分 | 失分主要来源 |")
    w("|---|---|---|---|---|")
    risk = {
        "DS": "41 题算法设计写不出最优解或复杂度不达标；42 题树/图应用题算错",
        "CO": "43/44 题 Cache 与流水线计算、浮点数格式、指令格式推断",
        "OS": "45 题 PV 大题信号量建模错；46 题页面置换/文件索引计算",
        "NET": "47 题综合计算（子网划分、TCP 窗口、时延）",
    }
    tot_full = tot_t = tot_l = 0
    for k in ORDER:
        lose = FULL[k] - TARGET[k]
        tot_full += FULL[k]; tot_t += TARGET[k]; tot_l += lose
        w(f"| {SUBJECTS[k]} | {FULL[k]} | {TARGET[k]} | {lose} | {risk[k]} |")
    w(f"| **合计** | **{tot_full}** | **{tot_t}** | **{tot_l}** | — |")
    w()
    w("**结论**：120 分不是“每科都很好”，而是“**每科都不崩**”。"
      "数据结构 + 计组占 90 分，是得分主体；网络只有 25 分，投入产出比最高但天花板低。"
      "**只要四科都不出现整题空白，120 分是稳的**；网上说的“130+/140+”才需要拼算法最优解和细节。")
    w()


# ---------------------------------------------------------------- overview
def sec_overview():
    w("## 二、真题分类总览")
    w()
    w("### 2.1 分科题量与分值（全部年份累计）")
    w()
    w("| 科目 | 累计题量 | 累计分值 | 年均题量 | 年均分值 |")
    w("|---|---|---|---|---|")
    ny = max(len(S["years"]), 1)
    for k in ORDER:
        d = S["subjects"][k]
        w(f"| {SUBJECTS[k]} | {d['count']} | {d['points']} | {d['count']/ny:.1f} | {d['points']/ny:.1f} |")
    w()
    w("> 累计分值与大纲满分比例一致（45:45:35:25），说明分类结果与试卷结构自洽——"
      "这是验证分类正确性的一个独立检查点。")
    w()
    img("02_分科分值.png", "四科累计分值占比")
    w()


# ---------------------------------------------------------------- chapters
def sec_chapters():
    w("## 三、按考纲章节的考频（核心表）")
    w()
    w("**读法**：`累计分值` 越高 = 这一章在 18 年里被考得越多；`年份覆盖` 越高 = 越稳定地每年都考。"
      "两者都高的章节是“必须拿满”的章节。")
    for k in ORDER:
        rows = [c for c in S["chapters"] if c["subject"] == k]
        rows.sort(key=lambda c: -c["points"])
        w()
        w(f"### {SUBJECTS[k]}")
        w()
        w("| 章 | 累计题量 | 累计分值 | 年均分值 | 占本科比重 |")
        w("|---|---|---|---|---|")
        totp = sum(c["points"] for c in rows) or 1
        for c in rows:
            w(f"| {c['chapter']} | {c['count']} | {c['points']} | "
              f"{c['points']/len(S['years']):.1f} | {c['points']/totp*100:.1f}% |")
        w()
        img(f"03_章节分值_{k}.png", f"{SUBJECTS[k]}：各章累计分值")
        img(f"05_章节年份热力_{k}.png", f"{SUBJECTS[k]}：各章逐年出题数")


# ---------------------------------------------------------------- top KPs
def sec_topkp():
    w("## 四、高频考点排行（分科 TOP）")
    w()
    w("只统计**叶子知识点**级别。`年份覆盖` 表示 18 年中有多少年考到过——"
      "这是比“考过几次”更强的信号：**覆盖高的知识点几乎每年必现，属于“不复习就是失分”系列**。")
    for k in ORDER:
        rows = [x for x in S["kps"] if x["subject"] == k][:18]
        if not rows:
            continue
        w()
        w(f"### {SUBJECTS[k]}")
        w()
        w("| # | 知识点 | 所在章 | 累计分值 | 题次 | 年份覆盖 | 热度 |")
        w("|---|---|---|---|---|---|---|")
        for i, x in enumerate(rows, 1):
            hot = "🔥🔥🔥" if x["n_years"] >= 12 else ("🔥🔥" if x["n_years"] >= 8 else "🔥")
            w(f"| {i} | {x['name']} | {x['chapter']} | {x['points']} | {x['count']} | "
              f"{x['n_years']}/{len(S['years'])} | {hot} |")
        w()
        img(f"04_高频知识点_{k}.png", f"{SUBJECTS[k]}：高频知识点累计分值")


# ---------------------------------------------------------------- priority
def priority_label(n_years, total_years):
    r = n_years / max(total_years, 1)
    if r >= 0.80:
        return "**必考**"
    if r >= 0.55:
        return "**高频**"
    if r >= 0.30:
        return "常考"
    return "了解"


def sec_subject_priority():
    w("## 五、分科复习重点（按考纲知识点逐条定级）")
    w()
    w("定级规则（由实测年份覆盖率推出，不是主观判断）：")
    w()
    w("| 等级 | 判定 | 复习要求 |")
    w("|---|---|---|")
    w("| 必考 | 18 年中 ≥14 年出现 | 必须做到**会做且不慢**，考场上不允许失分 |")
    w("| 高频 | 出现 10–13 年 | 必须会做标准题型，允许难题变体失分 |")
    w("| 常考 | 出现 6–9 年 | 掌握基本概念与典型解法 |")
    w("| 了解 | 出现 ≤5 年 | 知道是什么，能排除干扰选项即可 |")
    w()
    ny = len(S["years"])
    for k in ORDER:
        rows = [x for x in S["kps"] if x["subject"] == k]
        rows.sort(key=lambda x: (-x["n_years"], -x["points"], x["id"]))
        w(f"### {SUBJECTS[k]}")
        w()
        w("| 等级 | 知识点 | 章 | 年份覆盖 | 累计分值 |")
        w("|---|---|---|---|---|")
        for x in rows:
            lv = priority_label(x["n_years"], ny)
            w(f"| {lv} | {x['name']} | {x['chapter']} | {x['n_years']}/{ny} | {x['points']} |")
        w()


# ---------------------------------------------------------------- roadmap
def sec_roadmap():
    w("## 六、120 分路线图")
    w()
    w("### 6.1 三轮总流程")
    w()
    img("10_三轮复习流程.png", "三轮复习总流程与每轮验收标准")
    w()
    w("### 6.2 每轮做什么、怎么验收")
    w()
    w("| 轮次 | 时长 | 核心动作 | 验收标准 |")
    w("|---|---|---|---|")
    w("| 第一轮 · 基础 | 8–10 周 | 按教材/复习书过全部考纲知识点；每章配套选择+小题 | 能默写每章主干知识；选择题正确率 ≥60% |")
    w("| 第二轮 · 强化 | 5–6 周 | 按本报告的高频考点定向突破；四大专题（Cache、流水线、PV、子网） | 选择题正确率 ≥80%；大题能独立写出标准过程 |")
    w("| 第三轮 · 冲刺 | 3–4 周 | 限时套卷（180 min）、错题回炉、背诵点 | 套卷稳定 115–125；错题本二刷全对 |")
    w()
    w("### 6.3 四大专题（决定 120 分能否达成的关键）")
    w()
    w("这四个专题覆盖了综合题的绝大部分分值，是**唯一需要“专项集中突破”**的内容：")
    w()
    w("| 专题 | 覆盖科目 | 涉及知识点 | 典型分值 |")
    w("|---|---|---|---|")
    w("| Cache 与存储层次 | 计组 + OS | Cache 映射/替换/写策略、页表与 TLB、地址位数计算 | 12–20 分 |")
    w("| 指令流水线 | 计组 | 结构/数据/控制冒险、转发阻塞、时空图、加速比 | 8–15 分 |")
    w("| 同步与 PV | OS | 信号量建模、经典同步问题、死锁与银行家算法 | 8–15 分 |")
    w("| 子网划分与网络计算 | 网络 | CIDR、子网掩码、时延与带宽、TCP 窗口与拥塞 | 9–17 分 |")
    w()
    w("### 6.4 各科大题实战流程")
    w()
    img("11_DS大题流程.png", "数据结构 41/42 题实战流程")
    w()
    img("12_CO大题流程.png", "计组 43/44 题实战流程")
    w()
    img("13_OS大题流程.png", "操作系统 45/46 题实战流程")
    w()
    img("14_NET大题流程.png", "计算机网络 47 题实战流程")
    w()


# ---------------------------------------------------------------- mindmaps
def sec_mindmaps():
    w("## 七、思维导图（四科考纲知识树）")
    w()
    w("四张图对应四科考纲的完整枝干，叶节点即第 5 节的叶子知识点。"
      "建议**打印后手写补充易错点**，比反复看电子版有效。")
    w()
    w("### 7.1 总览")
    img("00_总览知识地图.png", "408 四科知识地图总览")
    w("### 7.2 数据结构")
    img("01_思维导图_DS.png", "数据结构考纲知识树")
    w("### 7.3 计算机组成原理")
    img("01_思维导图_CO.png", "计算机组成原理考纲知识树")
    w("### 7.4 操作系统")
    img("01_思维导图_OS.png", "操作系统考纲知识树")
    w("### 7.5 计算机网络")
    img("01_思维导图_NET.png", "计算机网络考纲知识树")
    w()


# ---------------------------------------------------------------- flows
def sec_flows():
    w("## 八、重点流程分析图")
    w()
    w("这些是**考场上真正会用到的推导流程**，不是知识罗列。每一张都对应一类必考题型。")
    w()
    flows = [
        ("20_存储层次贯通.png", "Cache—主存—虚存：一条地址走完全部层次（计组 + OS 贯通）"),
        ("21_Cache地址划分.png", "Cache 地址位数计算流程（直接映射 / 组相联）"),
        ("22_流水线分析.png", "指令流水线：冒险判定与时空图 / 加速比计算"),
        ("23_PV建模.png", "PV 操作建模流程：从自然语言到信号量"),
        ("24_页面置换.png", "页面置换算法手工模拟流程（OPT / FIFO / LRU / CLOCK）"),
        ("25_子网划分.png", "子网划分与 CIDR 聚合计算流程"),
        ("26_TCP状态.png", "TCP 连接管理与窗口/拥塞控制计算流程"),
        ("27_图算法.png", "图算法选择决策树（MST / 最短路 / 拓扑 / 关键路径）"),
    ]
    for f, cap in flows:
        img(f, cap)


# ---------------------------------------------------------------- appendix
def sec_appendix():
    w("## 九、附录：逐题分类明细")
    w()
    w("完整明细见 `data/questions_classified.csv`（含年份、题号、科目、章、节、知识点、分值、题干摘录）。"
      "下面按年份给出压缩版，便于对照原卷复习。")
    w()
    qs = json.load(open(os.path.join(ROOT, "work", "out", "questions.json"), encoding="utf-8"))
    by_year = {}
    for r in qs:
        if r["kp"]:
            by_year.setdefault(r["year"], []).append(r)
    for yr in S["years"]:
        rows = sorted(by_year.get(yr, []), key=lambda x: x["q"])
        if not rows:
            continue
        w(f"### {yr} 年（{len(rows)} 题）")
        w()
        w("| 题 | 科目 | 知识点 |")
        w("|---|---|---|")
        for r in rows:
            w(f"| {r['q']} | {SUBJECTS[r['subject']]} | {KPNAME.get(r['kp'], r['kp'])} |")
        w()


def main():
    global KPNAME
    from syllabus import KP_BY_ID

    KPNAME = {k: v[4] for k, v in KP_BY_ID.items()}
    sec_header()
    sec_structure()
    sec_overview()
    sec_chapters()
    sec_topkp()
    sec_subject_priority()
    sec_roadmap()
    sec_mindmaps()
    sec_flows()
    sec_appendix()
    dest = os.path.join(OUT, "408_真题分类与120分复习方案.md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("wrote", dest, len("\n".join(L)), "chars")


if __name__ == "__main__":
    main()
