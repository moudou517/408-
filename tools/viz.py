# -*- coding: utf-8 -*-
"""绘图引擎：408 思维导图 / 流程图（matplotlib，中文字体）。

提供：
  draw_mindmap(...)   横向层级思维导图
  draw_flow(...)      纵向流程图（含判定分支）
  draw_matrix(...)    热力图
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

CJK = ["Microsoft YaHei", "SimHei", "SimSun", "DengXian"]
plt.rcParams["font.sans-serif"] = CJK
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 10

# 四科统一配色
PALETTE = {
    "DS": {"main": "#1f6feb", "light": "#dbe9ff", "mid": "#8ab4f8"},
    "CO": {"main": "#d1453b", "light": "#ffe0dd", "mid": "#f28b82"},
    "OS": {"main": "#1e8e3e", "light": "#d9f2dd", "mid": "#81c995"},
    "NET": {"main": "#b06000", "light": "#ffeccc", "mid": "#fdd663"},
    "MIX": {"main": "#5f6368", "light": "#eceff1", "mid": "#bdc1c6"},
}


def _box(ax, x, y, w, h, text, fc, ec, fs=9, tc="#111", weight="normal",
         radius=0.02, lw=1.0, alpha=1.0, align="center"):
    p = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        linewidth=lw, facecolor=fc, edgecolor=ec, alpha=alpha, zorder=3,
    )
    ax.add_patch(p)
    if align == "left":
        ax.text(x - w / 2 + 1.2, y, text, ha="left", va="center", fontsize=fs,
                color=tc, fontweight=weight, zorder=4, linespacing=1.35)
    else:
        ax.text(x, y, text, ha="center", va="center", fontsize=fs,
                color=tc, fontweight=weight, zorder=4, linespacing=1.35)
    return p


def _arrow(ax, x1, y1, x2, y2, color, lw=1.1, style="-|>", ls="-", rad=0.0, zorder=2):
    a = FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=9,
        color=color, linewidth=lw, linestyle=ls, zorder=zorder,
        connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1,
    )
    ax.add_patch(a)


# ---------------------------------------------------------------- mind map
def draw_mindmap(title, root, branches, out_path, figsize=None,
                 subject="MIX", note=None, max_leaf_chars=30):
    """branches: [(章节名, [叶子1, 叶子2, ...], 分值提示), ...]

    竖向：每个叶子占一行，章与章之间留 gap；画布高度随内容自适应。
    """
    c = PALETTE[subject]
    n_b = len(branches)
    row_h = 1.0
    gap = 0.95                     # 章间空隙（行数）
    blocks = [len(b[1]) for b in branches]
    content = sum(blocks) + gap * (n_b - 1)
    top_pad, bot_pad = 4.6, 1.0    # 标题占位
    H = content + top_pad + bot_pad

    fig_w = 16.0
    fig_h = max(6.0, min(0.30 * H, 62))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, H)
    ax.axis("off")

    ax.text(47, H - 0.9, title, ha="center", va="top", fontsize=19,
            fontweight="bold", color=c["main"])
    if note:
        ax.text(47, H - 2.6, note, ha="center", va="top", fontsize=10,
                color="#5f6368", style="italic")

    root_x, root_w = 8.5, 13.5
    ch_x, ch_w = 25.5, 10.0
    lf_x, lf_w = 63.0, 52.0
    body_mid = bot_pad + content / 2.0 - gap * 0.0

    _box(ax, root_x, body_mid, root_w, min(5.0, 1.8 + 0.5 * n_b), root,
         c["main"], c["main"], fs=12.5, tc="white", weight="bold", radius=0.03)

    y_top = bot_pad + content
    for bi, b in enumerate(branches):
        name, leaves = b[0], b[1]
        share = b[2] if len(b) > 2 else None
        block_h = len(leaves) * row_h
        y_mid = y_top - block_h / 2.0

        label = name if not share else f"{name}\n{share}"
        _box(ax, ch_x, y_mid, ch_w, block_h * 0.94, label,
             c["mid"], c["main"], fs=10.5, weight="bold", radius=0.022)
        _arrow(ax, root_x + root_w / 2, body_mid, ch_x - ch_w / 2, y_mid,
               c["main"], lw=1.7, rad=0.04)

        for li, leaf in enumerate(leaves):
            ly = y_top - li * row_h - row_h / 2.0
            txt = leaf if len(leaf) <= max_leaf_chars else leaf[: max_leaf_chars - 1] + "…"
            _box(ax, lf_x, ly, lf_w, row_h * 0.80, txt,
                 c["light"], c["mid"], fs=9.2, radius=0.012, align="left")
            _arrow(ax, ch_x + ch_w / 2, y_mid, lf_x - lf_w / 2, ly,
                   c["mid"], lw=0.85, rad=0.015, zorder=1)
        y_top -= block_h + gap

    fig.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
    fig.savefig(out_path, dpi=170, facecolor="white", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------- flow chart
def draw_flow(title, nodes, out_path, figsize=(15, 20), subject="MIX",
              note=None, band=None):
    """nodes: [{'id','text','kind':'start|end|step|decide|note','color?'}]
    或边列表形式由 draw_flow_edges 处理。这里用线性主流程 + 可选分支。"""
    c = PALETTE[subject]
    n = len(nodes)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, n * 10 + 12)
    ax.axis("off")
    H = n * 10 + 12
    ax.text(50, H - 0.6, title, ha="center", va="top", fontsize=20,
            fontweight="bold", color=c["main"])
    if note:
        ax.text(50, H - 3.4, note, ha="center", va="top", fontsize=10.5,
                color="#5f6368", style="italic")

    y = H - 7.5
    cx = 38.0
    prev = None
    for nd in nodes:
        kind = nd.get("kind", "step")
        col = nd.get("color", None)
        if kind == "start":
            w, h, fc, ec, fs, wgt = 40, 4.4, c["main"], c["main"], 12.5, "bold"
            tc = "white"
        elif kind == "end":
            w, h, fc, ec, fs, wgt = 40, 4.4, "#202124", "#202124", 12.5, "bold"
            tc = "white"
        elif kind == "decide":
            w, h, fc, ec, fs, wgt = 50, 4.8, "#fff4e5", "#e37400", 10.5, "bold"
            tc = "#111"
        elif kind == "note":
            w, h, fc, ec, fs, wgt = 58, 3.4, "#f1f3f4", "#9aa0a6", 9.5, "normal"
            tc = "#3c4043"
        else:
            w, h, fc, ec, fs, wgt = 62, 4.2, col or c["light"], c["mid"], 10.0, "normal"
            tc = "#111"
        _box(ax, cx, y, w, h, nd["text"], fc, ec, fs=fs, weight=wgt, tc=tc,
             radius=0.02, lw=1.2)
        if prev is not None:
            _arrow(ax, cx, prev - 2.2, cx, y + 2.2, c["main"], lw=1.4)
        if nd.get("right"):
            _box(ax, 84, y, 26, 3.2, nd["right"], "#ffffff", c["mid"], fs=9.0)
            _arrow(ax, cx + w / 2, y, 71, y, c["mid"], lw=1.0, ls=(0, (4, 2)))
        prev = y
        y -= 10

    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------- matrix
def draw_matrix(title, rows, cols, matrix, out_path, figsize=(15, 9),
                xlabel="", ylabel="", cmap="YlOrRd", annot=True, fmt="{:.0f}"):
    fig, ax = plt.subplots(figsize=figsize)
    import numpy as np

    m = np.array(matrix, dtype=float)
    im = ax.imshow(m, cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=9)
    if annot:
        vmax = m.max() if m.size and m.max() > 0 else 1
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                v = m[i, j]
                if v > 0:
                    ax.text(j, i, fmt.format(v), ha="center", va="center",
                            fontsize=7.5, color="white" if v > 0.62 * vmax else "#222")
    ax.set_title(title, fontsize=15, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.75)
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------- bar
def draw_bars(title, labels, values, out_path, figsize=(14, 8), subject="MIX",
              xlabel="", horizontal=True, color_map=None, value_fmt="{:.0f}"):
    c = PALETTE[subject]
    fig, ax = plt.subplots(figsize=figsize)
    idx = range(len(labels))
    colors = [color_map.get(l, c["mid"]) if color_map else c["mid"] for l in labels]
    if horizontal:
        bars = ax.barh(list(idx), values, color=colors, edgecolor=c["main"], linewidth=0.6)
        ax.set_yticks(list(idx))
        ax.set_yticklabels(labels, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel, fontsize=10)
        for b, v in zip(bars, values):
            ax.text(b.get_width() + max(values) * 0.01, b.get_y() + b.get_height() / 2,
                    value_fmt.format(v), va="center", fontsize=8.5)
    else:
        bars = ax.bar(list(idx), values, color=colors, edgecolor=c["main"], linewidth=0.6)
        ax.set_xticks(list(idx))
        ax.set_xticklabels(labels, fontsize=9, rotation=40, ha="right")
        ax.set_ylabel(xlabel, fontsize=10)
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(values) * 0.01,
                    value_fmt.format(v), ha="center", fontsize=8.5)
    ax.set_title(title, fontsize=15, fontweight="bold", pad=12)
    ax.grid(axis="x" if horizontal else "y", linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path
