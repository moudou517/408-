# -*- coding: utf-8 -*-
"""Inject the richText() renderer (paragraphs + code blocks) into the page templates.

解析/题干里含 C 代码与表格，之前把空格压平后缩进全丢了。这里：
  * 在三个模板的 JS 里插入 richText / isCode / joinCJK
  * 在三个模板的 CSS 里插入 .rt 相关样式
  * 把渲染调用从 esc() 换成 richText()
"""

import re

FILES = {
    r"E:\CST\408\tools\make_bigq.py": "bigq",
    r"E:\CST\408\tools\make_quiz.py": "quiz",
    r"E:\CST\408\tools\make_browse.py": "browse",
}

JS = r"""
  /* ---- 段落 / 代码块渲染：保留换行与缩进，自动识别代码 ---- */
  function isCode(lines){
    const ls = lines.filter(function(l){ return l.trim(); });
    if(!ls.length) return false;
    if(ls.length === 1){
      const t = ls[0];
      return /[{};]\s*$/.test(t) && /[=<>()]|\[/.test(t) && t.trim().length > 6;
    }
    const hit = ls.filter(function(l){
      return /[{};]/.test(l) || /^\s{2,}\S/.test(l) ||
             /^\s*(for|while|if|else|return|int|void|char|struct|typedef|float|double|long|unsigned|printf|scanf|malloc|free|sizeof|push|pop)\b/.test(l);
    });
    if(hit.length >= Math.ceil(ls.length * 0.5)) return true;
    const short = ls.filter(function(l){ return l.trim().length <= 20; }).length;
    return ls.length >= 3 && short >= Math.ceil(ls.length * 0.7);
  }
  function joinCJK(lines){
    var out = '';
    lines.forEach(function(l){
      l = l.trim();
      if(!l) return;
      if(!out){ out = l; return; }
      var a = out.slice(-1), c = l.charAt(0);
      var cjkA = /[\u4e00-\u9fff，。；：、）】》？！]/.test(a);
      var cjkB = /[\u4e00-\u9fff（【《]/.test(c);
      out += (cjkA || cjkB) ? l : (' ' + l);
    });
    return out;
  }
  function richText(s){
    if(!s) return '';
    var raw = String(s).replace(/\t/g, '    ');
    var blocks = [], cur = [];
    raw.split('\n').forEach(function(ln){
      if(!ln.trim()){ if(cur.length){ blocks.push(cur); cur = []; } }
      else cur.push(ln);
    });
    if(cur.length) blocks.push(cur);
    return blocks.map(function(b){
      if(isCode(b)) return '<pre class="code">' + esc(b.join('\n')) + '</pre>';
      return '<p class="para">' + esc(joinCJK(b)) + '</p>';
    }).join('');
  }
"""

CSS = """
.rt p.para{margin:0 0 8px}
.rt p.para:last-child{margin-bottom:0}
.rt pre.code{margin:8px 0 12px;padding:10px 12px;background:#f7f4ec;border:1px solid var(--rule);
  border-left:3px solid var(--ac,#8a7f72);border-radius:3px;overflow-x:auto;
  font-family:var(--mono);font-size:12.4px;line-height:1.62;white-space:pre;color:#2b2622;
  -webkit-text-size-adjust:100%}
.rt{word-break:break-word}
"""

REPL = {
    "bigq": [
        ('<div class="stem">${esc(r.st)}</div>', '<div class="stem rt">${richText(r.st)}</div>'),
        ('<div class="solbody">${esc(r.sol)}</div>', '<div class="solbody rt">${richText(r.sol)}</div>'),
    ],
    "quiz": [
        ('${r.ex?`<p class="ex"><b>解析：</b>${esc(r.ex)}</p>`:\'\'}',
         '${r.ex?`<div class="ex rt"><b>解析：</b>${richText(r.ex)}</div>`:\'\'}'),
        ('<div class="stem">${esc(r.st)}</div>', '<div class="stem rt">${richText(r.st)}</div>'),
    ],
    "browse": [
        ("if(r.fs) parts.push('<div class=\"fs\">'+esc(r.fs)+'</div>');",
         "if(r.fs) parts.push('<div class=\"fs rt\">'+richText(r.fs)+'</div>');"),
        ('\'<div class="xbody"><b>\'+(r.t===1?\'参考答案与思路：\':\'解析：\')+\n            \'</b>\'+esc(r.x)+\'</div>\'',
         '\'<div class="xbody rt"><b>\'+(r.t===1?\'参考答案与思路：\':\'解析：\')+\n            \'</b>\'+richText(r.x)+\'</div>\''),
    ],
}

for path, kind in FILES.items():
    c = open(path, encoding="utf-8").read()
    if "function richText(" in c:
        print(f"{kind}: already patched")
        continue
    # 1) 注入 JS（放在 esc 定义之后；browse/quiz 有 esc，bigq 也有）
    m = re.search(r"\n(\s*)function esc\(s\).*?\n", c)
    if not m:
        print(f"{kind}: esc() not found, JS 未注入")
    else:
        c = c[:m.end()] + JS + c[m.end():]
    # 2) 注入 CSS（放在 </style> 前）
    if "</style>" in c:
        c = c.replace("</style>", CSS + "</style>", 1)
    # 3) 替换渲染调用
    n = 0
    for a, b in REPL[kind]:
        if a in c:
            c = c.replace(a, b)
            n += 1
        else:
            print(f"  {kind}: 未匹配 -> {a[:60]!r}")
    open(path, "w", encoding="utf-8").write(c)
    print(f"{kind}: JS+CSS 注入完成, 渲染替换 {n}/{len(REPL[kind])}")
