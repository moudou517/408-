# -*- coding: utf-8 -*-
"""Crop each question's figure(s) out of the exam PDFs and save as PNG.

408 的插图绝大多数是栅格图片（page.get_image_info 能拿到 bbox），所以：
  1) 找出每一页上每道题题号行的位置，得到「题号 → 纵向区间」
  2) 落在该区间里的图片，取并集裁剪成一张 PNG
  3) 同时处理「选项就是图片」的情况（同样落在区间内）

输出：out/qimg/{year}_{q}.png  与  out/data/figures.json
"""

import json
import os
import re
import sys

import pymupdf

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
IMG = os.path.join(OUT, "qimg")
os.makedirs(IMG, exist_ok=True)

DPI = 200
PAD = 6.0            # 裁剪留白（pt）
MIN_SIDE = 24.0      # 太小的图（分隔线、图标）忽略
MAX_RATIO = 0.82     # 超过页面这个比例认为是背景/整页扫描


def pdf_of(year):
    hits = []
    for dirpath, _d, files in os.walk(ROOT):
        if ".pylibs" in dirpath or ".tmp" in dirpath or os.sep + "work" in dirpath:
            continue
        for f in files:
            if not f.lower().endswith(".pdf") or "解析" in f:
                continue
            m = re.search(r"(19|20)\d{2}", f)
            if m and m.group(0) == str(year):
                hits.append(os.path.join(dirpath, f))
    return hits[0] if hits else None


QRE = re.compile(r"^\s*(\d{1,2})\s*[.．、]")


def question_bands(page):
    """[(qnum, y_top)] for question-number lines on this page, sorted by y."""
    out = []
    d = page.get_text("dict")
    for blk in d.get("blocks", []):
        if blk.get("type") != 0:
            continue
        for line in blk.get("lines", []):
            txt = "".join(s.get("text", "") for s in line.get("spans", []))
            m = QRE.match(txt)
            if not m:
                continue
            q = int(m.group(1))
            if not (1 <= q <= 47):
                continue
            out.append((q, line["bbox"][1]))
    out.sort(key=lambda t: t[1])
    # 同题号取第一次出现
    seen, uniq = set(), []
    for q, y in out:
        if q in seen:
            continue
        seen.add(q)
        uniq.append((q, y))
    return uniq


def images_on(page):
    """Raster image bboxes, filtered to plausible figures."""
    w, h = page.rect.width, page.rect.height
    out = []
    for info in page.get_image_info():
        x0, y0, x1, y1 = info["bbox"]
        bw, bh = x1 - x0, y1 - y0
        if bw < MIN_SIDE or bh < MIN_SIDE:
            continue
        if bw * bh > MAX_RATIO * w * h:
            continue
        out.append(pymupdf.Rect(x0, y0, x1, y1))
    return out


def drawings_on(page):
    """Vector drawings (结点图、指令格式表、树形图…) 的包围盒。"""
    w, h = page.rect.width, page.rect.height
    out = []
    for d in page.get_drawings():
        r = pymupdf.Rect(d["rect"])
        if r.is_empty:
            continue
        if r.width < 0.4 and r.height < 0.4:
            continue
        # 页眉页脚那种贯穿全页的细线
        if r.width > 0.90 * w and r.height < 3.0:
            continue
        out.append(r)
    return out


def figure_rects(page, band_lo, band_hi):
    """某一题区间内的图形：栅格图 + 矢量图，返回需要裁剪的矩形列表。"""
    page_h = page.rect.height
    rects = [r for r in images_on(page) if band_lo <= (r.y0 + r.y1) / 2 <= band_hi]
    # 矢量图形按区间裁剪
    dr = [r for r in drawings_on(page)
          if band_lo <= (r.y0 + r.y1) / 2 <= band_hi]
    if dr:
        u = pymupdf.Rect(min(r.x0 for r in dr), min(r.y0 for r in dr),
                         max(r.x1 for r in dr), max(r.y1 for r in dr))
        # 过滤掉"只是一条线/太小/几乎整页"的并集
        if u.width >= 40 and u.height >= 14 and u.height < 0.60 * page_h \
                and (u.width * u.height) < MAX_RATIO * page.rect.width * page_h:
            rects.extend(dr)
    return rects


def crop_union(page, rects, dest):
    """Crop the union of rects (with padding) to a PNG."""
    x0 = min(r.x0 for r in rects)
    y0 = min(r.y0 for r in rects)
    x1 = max(r.x1 for r in rects)
    y1 = max(r.y1 for r in rects)
    clip = pymupdf.Rect(max(0, x0 - PAD), max(0, y0 - PAD),
                        page.rect.width, min(page.rect.height, y1 + PAD))
    clip.x1 = min(page.rect.width, x1 + PAD)
    pm = page.get_pixmap(dpi=DPI, clip=clip)
    pm.save(dest)
    return clip.width, clip.height, os.path.getsize(dest)


def main():
    years = [int(x) for x in sys.argv[1:]] or list(range(2009, 2027))
    figures = {}
    stats = []
    for year in years:
        p = pdf_of(year)
        if not p:
            print(f"{year}: no pdf")
            continue
        doc = pymupdf.open(p)
        n_ok = 0
        for pi, page in enumerate(doc):
            bands = question_bands(page)
            if not bands:
                continue
            imgs = images_on(page)
            if not imgs:
                continue
            page_h = page.rect.height
            for i, (q, y) in enumerate(bands):
                y_end = bands[i + 1][1] if i + 1 < len(bands) else page_h + 1
                # 允许图形略高于题号行（排版常把图放在题干上方）
                y_lo = y - 40
                inside = figure_rects(page, y_lo, y_end)
                if not inside:
                    continue
                key = f"{year}-{q}"
                if key in figures:          # 跨页续图：并进已有结果
                    continue
                dest = os.path.join(IMG, f"{year}_{q}.png")
                try:
                    w, h, size = crop_union(page, inside, dest)
                except Exception as e:
                    print(f"  crop fail {key}: {type(e).__name__}")
                    continue
                figures[key] = f"qimg/{year}_{q}.png"
                n_ok += 1
        doc.close()
        stats.append((year, n_ok))
        print(f"{year}: {n_ok} 张图", flush=True)

    dest = os.path.join(OUT, "data", "figures.json")
    json.dump(figures, open(dest, "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    print(f"\n共 {len(figures)} 张 -> {dest}")
    print("按年份:", dict(stats))


if __name__ == "__main__":
    main()
