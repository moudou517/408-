# -*- coding: utf-8 -*-
"""Generate two tablet-friendly PDFs:

  1. 408_题库索引.pdf   — clickable index: KP目录 -> 题目列表 -> 年份题录 (internal links)
  2. 408_图表集.pdf     — all figures, one per page

Everything is offline-safe: any PDF reader (iPad 图书 / GoodNotes / PDF Expert) can open it.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,  # noqa: E402
                               PageBreak, PageTemplate, Paragraph, Spacer, Table,
                               TableStyle)

from syllabus import KP_BY_ID, SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
FIG = os.path.join(OUT, "fig")

COMPOSITE_POINTS = {41: 13, 42: 10, 43: 13, 44: 10, 45: 8, 46: 7, 47: 9}
SUBJ_ORDER = ["DS", "CO", "OS", "NET"]
INK = colors.HexColor("#1a1613")
INK2 = colors.HexColor("#4a423a")
INK3 = colors.HexColor("#8a7f72")
RULE = colors.HexColor("#d8cfbe")
ACC = {
    "DS": colors.HexColor("#1f5fa8"),
    "CO": colors.HexColor("#a83226"),
    "OS": colors.HexColor("#1c6b3c"),
    "NET": colors.HexColor("#96650a"),
}

# ---------------------------------------------------------------- fonts
FONTS = {}


def register_fonts():
    def add(name, path, idx=None):
        try:
            if idx is None:
                pdfmetrics.registerFont(TTFont(name, path))
            else:
                pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx))
            return True
        except Exception as e:
            print(f"  font {name} failed: {e}")
            return False

    ok = False
    for p, i in ((r"C:\Windows\Fonts\simsun.ttc", 0), (r"C:\Windows\Fonts\msyh.ttc", 0)):
        if os.path.exists(p) and add("CJK", p, i):
            ok = True
            FONTS["body"] = "CJK"
            break
    for p in (r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\msyhbd.ttc"):
        if os.path.exists(p) and add("CJKH", p, None if p.endswith(".ttf") else 0):
            FONTS["bold"] = "CJKH"
            break
    if not ok:
        r = os.path.join(ROOT, ".pylibs", "reportlab", "fonts", "Vera.ttf")
        if os.path.exists(r):
            add("CJK", r)
            FONTS.update({"body": "CJK", "bold": "CJK"})
    FONTS.setdefault("bold", FONTS.get("body", "Helvetica"))
    print(f"  fonts: body={FONTS.get('body')} bold={FONTS.get('bold')}")
    return FONTS


def styles():
    B, BOLD = FONTS["body"], FONTS["bold"]
    s = {}
    s["title"] = ParagraphStyle("title", fontName=BOLD, fontSize=21, leading=29,
                                textColor=INK, spaceAfter=4, alignment=TA_CENTER)
    s["sub"] = ParagraphStyle("sub", fontName=B, fontSize=10, leading=15,
                              textColor=INK3, alignment=TA_CENTER, spaceAfter=2)
    s["h1"] = ParagraphStyle("h1", fontName=BOLD, fontSize=14.5, leading=21,
                             textColor=INK, spaceBefore=13, spaceAfter=5)
    s["h2"] = ParagraphStyle("h2", fontName=BOLD, fontSize=11.5, leading=17,
                             textColor=INK, spaceBefore=9, spaceAfter=3)
    s["body"] = ParagraphStyle("body", fontName=B, fontSize=9.2, leading=14.4,
                               textColor=INK, wordWrap="CJK", spaceAfter=2)
    s["small"] = ParagraphStyle("small", fontName=B, fontSize=8.1, leading=12.4,
                                textColor=INK2, wordWrap="CJK", spaceAfter=1)
    s["idx"] = ParagraphStyle("idx", fontName=B, fontSize=9.0, leading=13.6,
                              textColor=INK, wordWrap="CJK")
    s["kpt"] = ParagraphStyle("kpt", fontName=BOLD, fontSize=12.5, leading=18,
                              textColor=INK, spaceBefore=2, spaceAfter=3)
    s["cap"] = ParagraphStyle("cap", fontName=B, fontSize=9, leading=14,
                              textColor=INK3, alignment=TA_CENTER, spaceAfter=6)
    return s


# ---------------------------------------------------------------- data
def points_of(q):
    return 2 if q <= 40 else COMPOSITE_POINTS.get(q, 2)


def load():
    rows = json.load(open(os.path.join(ROOT, "work", "out", "questions.json"), encoding="utf-8"))
    keep = [r for r in rows if r["kp"]]
    summary = json.load(open(os.path.join(OUT, "data", "summary.json"), encoding="utf-8"))
    return keep, summary


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def clip(t, n):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1] + "…"


# ---------------------------------------------------------------- index pdf
def build_index_pdf(rows, summary, dest):
    st = styles()
    B, BOLD = FONTS["body"], FONTS["bold"]
    ny = len(summary["years"])

    # group by KP
    by_kp = {}
    for r in rows:
        by_kp.setdefault(r["kp"], []).append(r)
    for v in by_kp.values():
        v.sort(key=lambda x: (x["year"], x["q"]))

    # order KPs: subject -> chapter -> points desc
    ordered = []
    for s in SUBJ_ORDER:
        ks = [k for k in summary["kps"] if k["subject"] == s]
        chapters = []
        for k in ks:
            if k["chapter"] not in chapters:
                chapters.append(k["chapter"])
        chap_pts = {c["chapter"]: c["points"] for c in summary["chapters"] if c["subject"] == s}
        chapters.sort(key=lambda c: -chap_pts.get(c, 0))
        for c in chapters:
            for k in [x for x in ks if x["chapter"] == c]:
                ordered.append(k)

    story = []
    story.append(Paragraph("408 真题题库索引", st["title"]))
    story.append(Paragraph("按考纲知识点检索 · 2009–2026 · 全 18 套卷", st["sub"]))
    story.append(Paragraph(
        "蓝色文字可点击跳转（目录 → 知识点 → 题目；每节末尾可跳回目录）", st["sub"]))
    story.append(Spacer(1, 7 * mm))

    # ---- overview table
    story.append(Paragraph("一、分科总览", st["h1"]))
    data = [["科目", "题量", "累计分值", "年均分值", "大纲满分"]]
    full = {"DS": 45, "CO": 45, "OS": 35, "NET": 25}
    for s in SUBJ_ORDER:
        d = summary["subjects"][s]
        data.append([SUBJECTS[s], str(d["count"]), str(d["points"]),
                     f"{d['points']/ny:.1f}", str(full[s])])
    t = Table(data, colWidths=[46 * mm, 22 * mm, 26 * mm, 26 * mm, 26 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), B),
        ("FONTNAME", (0, 0), (-1, 0), BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#efe8db")),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))

    # ---- chapter table
    story.append(Paragraph("二、各章累计分值", st["h1"]))
    data = [["科目", "章", "题量", "累计分值", "年均"]]
    seen = set()
    for s in SUBJ_ORDER:
        for c in sorted([x for x in summary["chapters"] if x["subject"] == s],
                        key=lambda x: -x["points"]):
            data.append([SUBJECTS[s], c["chapter"], str(c["count"]), str(c["points"]),
                         f"{c['points']/ny:.1f}"])
    t = Table(data, colWidths=[34 * mm, 52 * mm, 20 * mm, 26 * mm, 20 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), B),
        ("FONTNAME", (0, 0), (-1, 0), BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 8.4),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#efe8db")),
        ("LINEBELOW", (0, 0), (-1, -1), 0.35, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ---- clickable KP directory
    story.append(Paragraph('<a name="toc"/>三、知识点目录（点击跳转）', st["h1"]))
    story.append(Paragraph(
        "格式：知识点 ······ 题次 / 累计分值 ······ 年份覆盖", st["small"]))
    story.append(Spacer(1, 2 * mm))

    cur_subj = None
    for k in ordered:
        if k["subject"] != cur_subj:
            cur_subj = k["subject"]
            story.append(Paragraph(
                f'<font color="#{ACC[cur_subj].hexval()[2:]}"><b>{SUBJECTS[cur_subj]}</b></font>',
                st["h2"]))
        anchor = "kp-" + k["id"].replace(".", "_")
        line = (f'<a href="#{anchor}" color="#1f5fa8">{esc(k["name"])}</a>'
                f' &nbsp;<font size="7.4" color="#8a7f72">{k["count"]} 题 / {k["points"]} 分'
                f' · {k["n_years"]}/{ny} 年</font>')
        story.append(Paragraph(line, st["idx"]))

    # ---- per-KP sections
    story.append(PageBreak())
    story.append(Paragraph("四、按知识点 · 全部题目", st["h1"]))
    story.append(Paragraph('点每节标题右侧「↑ 目录」可返回上页索引。', st["small"]))

    for k in ordered:
        kid = k["id"]
        anchor = "kp-" + kid.replace(".", "_")
        items = by_kp.get(kid, [])
        if not items:
            continue
        head = (f'<a name="{anchor}"/>'
                f'<font color="#{ACC[k["subject"]].hexval()[2:]}">■</font> {esc(k["name"])}'
                f' &nbsp;<font size="8" color="#8a7f72">{kid} · 所在章：{esc(k["chapter"])}'
                f' · {len(items)} 题 / {sum(points_of(i["q"]) for i in items)} 分</font>'
                f' &nbsp;&nbsp;<a href="#toc" color="#1f5fa8" size="8">↑ 目录</a>')
        blk = [Paragraph(head, st["kpt"])]
        for r in items:
            typ = "综合" if r["q"] > 40 else "选择"
            blk.append(Paragraph(
                f'<font name="{BOLD}" color="#1a1613">{r["year"]}-{r["q"]}</font>'
                f'<font size="7.6" color="#8a7f72"> [{typ} {points_of(r["q"])}分] </font>'
                f'{esc(clip(r["stem"], 86))}', st["small"]))
        blk.append(Spacer(1, 4.5 * mm))
        story.append(KeepTogether(blk))

    # ---- by year
    story.append(PageBreak())
    story.append(Paragraph("五、按年份 · 题录速查", st["h1"]))
    by_year = {}
    for r in rows:
        by_year.setdefault(r["year"], []).append(r)
    for y in sorted(by_year):
        items = sorted(by_year[y], key=lambda x: x["q"])
        blk = [Paragraph(f'<a name="y{y}"/>{y} 年 &nbsp;'
                         f'<font size="8" color="#8a7f72">{len(items)} 题 / '
                         f'{sum(points_of(i["q"]) for i in items)} 分</font>', st["h2"])]
        for r in items:
            kn = KP_BY_ID[r["kp"]][4]
            typ = "综" if r["q"] > 40 else "选"
            blk.append(Paragraph(
                f'<font name="{BOLD}">{r["q"]:>2}</font>'
                f'<font size="7.6" color="#8a7f72"> {typ}{points_of(r["q"])} </font>'
                f'{esc(kn)}', st["small"]))
        blk.append(Spacer(1, 4 * mm))
        story.append(KeepTogether(blk))

    build_doc(dest, story, "408 真题题库索引 · 2009–2026")
    return dest


def build_doc(dest, story, header_text):
    B = FONTS["body"]

    def on_page(canv, doc):
        canv.saveState()
        canv.setFont(B, 7.6)
        canv.setFillColor(INK3)
        canv.drawString(20 * mm, 12 * mm, header_text)
        canv.drawRightString(A4[0] - 20 * mm, 12 * mm, str(doc.page))
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.4)
        canv.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
        canv.restoreState()

    doc = BaseDocTemplate(dest, pagesize=A4,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=20 * mm,
                          title=header_text, author="DSH")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    doc.build(story)


# ---------------------------------------------------------------- figures pdf
FIG_LIST = [
    ("00_总览知识地图.png", "408 四科知识地图总览（分值 = 2009–2026 真题实测）"),
    ("01_思维导图_DS.png", "数据结构 · 考纲知识树（【必】=14 年以上考到，【高】=10–13 年）"),
    ("01_思维导图_CO.png", "计算机组成原理 · 考纲知识树"),
    ("01_思维导图_OS.png", "操作系统 · 考纲知识树"),
    ("01_思维导图_NET.png", "计算机网络 · 考纲知识树"),
    ("02_分科分值.png", "四科累计分值"),
    ("03_章节分值_DS.png", "数据结构：各章累计分值"),
    ("03_章节分值_CO.png", "计算机组成原理：各章累计分值"),
    ("03_章节分值_OS.png", "操作系统：各章累计分值"),
    ("03_章节分值_NET.png", "计算机网络：各章累计分值"),
    ("05_章节年份热力_DS.png", "数据结构：各章逐年出题数"),
    ("05_章节年份热力_CO.png", "计算机组成原理：各章逐年出题数"),
    ("05_章节年份热力_OS.png", "操作系统：各章逐年出题数"),
    ("05_章节年份热力_NET.png", "计算机网络：各章逐年出题数"),
    ("04_高频知识点_DS.png", "数据结构：高频知识点"),
    ("04_高频知识点_CO.png", "计算机组成原理：高频知识点"),
    ("04_高频知识点_OS.png", "操作系统：高频知识点"),
    ("04_高频知识点_NET.png", "计算机网络：高频知识点"),
    ("10_三轮复习流程.png", "三轮复习总流程与验收标准"),
    ("11_DS大题流程.png", "数据结构 41/42 题实战流程"),
    ("12_CO大题流程.png", "计组 43/44 题实战流程"),
    ("13_OS大题流程.png", "操作系统 45/46 题实战流程"),
    ("14_NET大题流程.png", "计算机网络 47 题实战流程"),
    ("20_存储层次贯通.png", "存储层次贯通：Cache—主存—虚拟存储"),
    ("21_Cache地址划分.png", "Cache 地址位数计算流程"),
    ("22_流水线分析.png", "指令流水线分析流程"),
    ("23_PV建模.png", "PV 操作建模流程"),
    ("24_页面置换.png", "页面置换算法手工模拟"),
    ("25_子网划分.png", "子网划分与 CIDR 计算"),
    ("26_TCP状态.png", "TCP 计算流程"),
    ("27_图算法.png", "图算法选择决策树"),
]


def build_figures_pdf(dest):
    from PIL import Image as PILImage

    st = styles()
    story = [
        Paragraph("408 复习图表集", st["title"]),
        Paragraph("思维导图 · 统计图 · 流程分析图 · 共 %d 张" % len(FIG_LIST), st["sub"]),
        Paragraph("建议在 iPad 上横屏阅读；GoodNotes / PDF Expert 可直接批注。", st["sub"]),
        PageBreak(),
    ]
    maxw = A4[0] - 44 * mm
    maxh = A4[1] - 62 * mm
    for i, (fn, cap) in enumerate(FIG_LIST, 1):
        p = os.path.join(FIG, fn)
        if not os.path.exists(p):
            continue
        with PILImage.open(p) as im:
            w, h = im.size
        scale = min(maxw / w, maxh / h, 1.0)
        img = Image(p, width=w * scale, height=h * scale)
        story.append(KeepTogether([
            Paragraph(f'<font color="#8a7f72" size="8">图 {i}/{len(FIG_LIST)}</font>', st["cap"]),
            img,
            Paragraph(esc(cap), st["cap"]),
        ]))
        story.append(PageBreak())

    build_doc(dest, story, "408 复习图表集")
    return dest


def main():
    register_fonts()
    rows, summary = load()
    p1 = build_index_pdf(rows, summary, os.path.join(OUT, "408_题库索引.pdf"))
    print("  ->", p1, f"{os.path.getsize(p1)/1e6:.2f} MB")
    p2 = build_figures_pdf(os.path.join(OUT, "408_图表集.pdf"))
    print("  ->", p2, f"{os.path.getsize(p2)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
