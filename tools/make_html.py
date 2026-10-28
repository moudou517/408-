# -*- coding: utf-8 -*-
"""Convert the generated Markdown report into a single self-contained HTML file.

Images are inlined as base64 so the HTML can be moved/printed without the fig/ folder.
"""

import base64
import html
import os
import re

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
SRC = os.path.join(OUT, "408_真题分类与120分复习方案.md")
DST = os.path.join(OUT, "408_真题分类与120分复习方案.html")

CSS = """
:root{--fg:#1f2328;--muted:#57606a;--line:#d0d7de;--accent:#1f6feb;--bg:#fff;}
*{box-sizing:border-box}
body{margin:0;background:#f6f8fa;color:var(--fg);
 font-family:"Microsoft YaHei","PingFang SC","Hiragino Sans GB",system-ui,sans-serif;
 line-height:1.75;font-size:15.5px;}
.wrap{max-width:1080px;margin:0 auto;padding:36px 44px 90px;background:var(--bg);
 box-shadow:0 1px 3px rgba(0,0,0,.08);}
h1{font-size:30px;line-height:1.3;margin:8px 0 22px;padding-bottom:14px;border-bottom:3px solid var(--accent);}
h2{font-size:23px;margin:44px 0 14px;padding-left:12px;border-left:5px solid var(--accent);}
h3{font-size:18.5px;margin:30px 0 10px;color:#0b3d91;}
p{margin:10px 0;}
blockquote{margin:14px 0;padding:10px 18px;background:#f0f6ff;border-left:4px solid #79a6f2;color:#243b53;}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px;display:block;overflow-x:auto;}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top;}
th{background:#eef3fb;font-weight:600;}
tr:nth-child(even) td{background:#fafbfc;}
img{max-width:100%;height:auto;display:block;margin:16px auto;border:1px solid var(--line);border-radius:6px;}
code{background:#f2f4f7;padding:1px 5px;border-radius:4px;font-size:13.5px;
 font-family:Consolas,"Courier New",monospace;}
hr{border:0;border-top:1px solid var(--line);margin:34px 0;}
ul,ol{margin:10px 0 10px 22px;}
.toc{background:#f7f9fc;border:1px solid var(--line);border-radius:8px;padding:14px 20px;margin:22px 0 34px;}
.toc b{display:block;margin-bottom:8px;color:var(--muted);font-size:13px;letter-spacing:1px;}
.toc a{color:var(--accent);text-decoration:none;display:block;padding:2px 0;font-size:14.5px;}
.toc a:hover{text-decoration:underline;}
.toc a.l2{padding-left:16px;color:#3c4043;}
.navbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:0 0 26px;
 padding:11px 16px;background:#eef3fb;border:1px solid #cfe0f7;border-radius:8px;font-size:13.5px;}
.navbar b{color:var(--muted);font-size:12px;font-weight:600;letter-spacing:.5px;margin-right:2px;}
.navbar a{color:var(--accent);text-decoration:none;padding:3px 10px;border:1px solid #b9d2f5;
 border-radius:999px;background:#fff;}
.navbar a:hover{background:var(--accent);color:#fff;border-color:var(--accent);}
.navbar a.cur{background:#dbe9ff;border-color:#a8c8f0;color:#0b3d91;cursor:default;}
em.strong-red{color:#c62828;font-weight:600;}
@media print{body{background:#fff}.wrap{box-shadow:none;max-width:none;padding:0}}
"""


def img_tag(src, alt):
    path = os.path.join(OUT, src.replace("/", os.sep))
    if not os.path.exists(path):
        return f"<p style='color:#c00'>[missing image: {html.escape(src)}]</p>"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return (f'<img alt="{html.escape(alt)}" src="data:image/png;base64,{b64}">')


def inline(text):
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def convert(md):
    lines = md.split("\n")
    out = []
    i = 0
    headings = []
    while i < len(lines):
        ln = lines[i]
        # image
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln.strip())
        if m:
            out.append(img_tag(m.group(2), m.group(1)))
            i += 1
            continue
        # table
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in header]
            t.append("</tr></thead><tbody>")
            for r in body:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue
        # headings
        mh = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if mh:
            lvl = len(mh.group(1))
            txt = mh.group(2)
            anchor = ""
            if lvl in (2, 3):
                aid = re.sub(r"[^\w\u4e00-\u9fff]+", "-", txt)[:60]
                anchor = f' id="{aid}"'
                headings.append((lvl, txt, aid))
            out.append(f"<h{lvl}{anchor}>{inline(txt)}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^---+$", ln.strip()):
            out.append("<hr>")
            i += 1
            continue
        if ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").rstrip())
                i += 1
            out.append("<blockquote>" + "<br>".join(inline(x) for x in buf) + "</blockquote>")
            continue
        if ln.strip() == "":
            out.append("")
            i += 1
            continue
        if re.match(r"^<p align", ln.strip()):
            out.append(ln)
            i += 1
            continue
        if ln.strip().startswith(("- ", "* ")):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                buf.append("<li>" + inline(lines[i].strip()[2:]) + "</li>")
                i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue
        out.append("<p>" + inline(ln) + "</p>")
        i += 1
    return "\n".join(out), headings


def main():
    md = open(SRC, encoding="utf-8").read()
    body, headings = convert(md)
    toc = ['<div class="toc"><b>目录</b>']
    for lvl, txt, aid in headings:
        cls = "l2" if lvl >= 3 else ""
        toc.append(f'<a class="{cls}" href="#{aid}">{html.escape(txt)}</a>')
    toc.append("</div>")
    navbar = (
        '<div class="navbar"><b>资料导航</b>'
        '<a href="index.html">入口页</a>'
        '<a href="map.html">知识体系</a>'
        '<a href="quiz.html">刷选择题</a>'
        '<a href="bigq.html">刷大题</a>'
        '<a href="browse.html">题库</a>'
        '<a class="cur">完整报告</a>'
        '<a href="408_题库索引.pdf">题库索引 PDF</a>'
        '<a href="408_图表集.pdf">图表集 PDF</a>'
        "</div>"
    )
    doc = (
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>408 真题考纲分类与 120 分复习方案</title>"
        f"<style>{CSS}</style></head><body><div class='wrap'>"
        + navbar
        + "\n".join(toc)
        + body
        + "</div></body></html>"
    )
    with open(DST, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", DST, f"{len(doc)/1e6:.1f} MB, {len(headings)} headings")


if __name__ == "__main__":
    main()
