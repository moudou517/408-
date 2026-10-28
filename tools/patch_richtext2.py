# -*- coding: utf-8 -*-
"""Second pass: inject richText into bigq (esc is an arrow fn) and fix browse's fs."""

import re

JS = open(r"E:\CST\408\tools\patch_richtext.py", encoding="utf-8").read()
m = re.search(r'JS = r"""(.*?)"""', JS, re.S)
JS_CODE = m.group(1)

# ---------- bigq ----------
p = r"E:\CST\408\tools\make_bigq.py"
c = open(p, encoding="utf-8").read()
if "function richText(" not in c:
    anchor = "  const esc=s=>String(s).replace("
    i = c.find(anchor)
    if i >= 0:
        j = c.find("\n", i)
        c = c[: j + 1] + JS_CODE + c[j + 1:]
        open(p, "w", encoding="utf-8").write(c)
        print("bigq: JS 已注入")
    else:
        print("bigq: 仍未找到插入点")
else:
    print("bigq: 已有 richText")

# ---------- browse: fs 行 ----------
p2 = r"E:\CST\408\tools\make_browse.py"
c2 = open(p2, encoding="utf-8").read()
old = """if(r.t===1 && r.fs) parts.push('<div class="fs">'+esc(r.fs)+'</div>');"""
new = """if(r.t===1 && r.fs) parts.push('<div class="fs rt">'+richText(r.fs)+'</div>');"""
if old in c2:
    c2 = c2.replace(old, new)
    open(p2, "w", encoding="utf-8").write(c2)
    print("browse: fs 已改为 richText")
else:
    print("browse: fs 行仍未匹配")
