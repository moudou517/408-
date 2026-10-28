# -*- coding: utf-8 -*-
"""Build an interactive browse page for the classified 408 questions.

Output: out/browse.html — a single self-contained file (data embedded),
with a Feishu-style outline sidebar, search, filters and deep links.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from syllabus import KP_BY_ID, SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")
SRC = os.path.join(ROOT, "work", "out", "questions.json")

COMPOSITE_POINTS = {41: 13, 42: 10, 43: 13, 44: 10, 45: 8, 46: 7, 47: 9}
SUBJ_ORDER = ["DS", "CO", "OS", "NET"]
CHAP_ORDER = {}

CHAPTER_ORDER = {
    "DS": ["绪论", "线性表", "栈、队列和数组", "串", "树与二叉树", "图", "查找", "排序"],
    "CO": ["计算机系统概述", "数据的表示和运算", "存储器层次结构", "指令系统",
           "中央处理器", "总线与输入输出"],
    "OS": ["操作系统概述", "进程管理", "内存管理", "文件管理", "输入输出管理"],
    "NET": ["计算机网络概述", "物理层", "数据链路层", "网络层", "传输层", "应用层"],
}


def points_of(q):
    return 2 if q <= 40 else COMPOSITE_POINTS.get(q, 2)


def load_rows():
    rows = json.load(open(SRC, encoding="utf-8"))

    # 选择题：选项 / 答案 / 解析
    qz = {}
    qp = os.path.join(OUT, "data", "quiz.json")
    if os.path.exists(qp):
        for r in json.load(open(qp, encoding="utf-8")):
            qz[(r["y"], r["q"])] = r
    # 综合题：参考答案与思路
    bg = {}
    bp = os.path.join(OUT, "data", "bigq.json")
    if os.path.exists(bp):
        for r in json.load(open(bp, encoding="utf-8")):
            bg[(r["y"], r["q"])] = r
    # 插图（从原卷裁出来的图 / 原卷切片）
    fg = {}
    fp = os.path.join(OUT, "data", "figures.json")
    if os.path.exists(fp):
        raw = json.load(open(fp, encoding="utf-8"))
        fg = {k: (v if isinstance(v, dict) else {"p": v, "scan": False})
              for k, v in raw.items()}

    out = []
    for r in rows:
        if not r["kp"]:
            continue
        k = KP_BY_ID[r["kp"]]
        stem = re.sub(r"\s+", " ", r["stem"]).strip()
        stem = re.sub(r"([A-D])[.．、]\s*", r"\1. ", stem)
        key = (r["year"], r["q"])
        item = {
            "y": r["year"],
            "q": r["q"],
            "t": 0 if r["q"] <= 40 else 1,
            "s": k[1],
            "ch": k[2],
            "sec": k[3],
            "kp": r["kp"],
            "kn": k[4],
            "p": points_of(r["q"]),
            "st": stem[:150],
        }
        q = qz.get(key)
        if q:
            item["o"] = q["op"]
            item["a"] = q["a"]
            if q.get("ex"):
                item["x"] = q["ex"]
        b = bg.get(key)
        if b and b.get("sol"):
            item["x"] = b["sol"]           # 综合题用「参考答案与思路」
            if b.get("st"):
                item["fs"] = b["st"]       # 完整题干
        f = fg.get(f'{r["year"]}-{r["q"]}')
        if f:
            item["im"] = f["p"]
            if f.get("scan"):
                item["imscan"] = 1
        out.append(item)
    out.sort(key=lambda x: (x["y"], x["q"]))
    return out


def build_tree(rows):
    """subject -> chapter -> kp, with counts/points."""
    tree = {}
    for s in SUBJ_ORDER:
        tree[s] = {}
    for r in rows:
        ch = tree[r["s"]].setdefault(r["ch"], {})
        node = ch.setdefault(r["kp"], {"name": r["kn"], "n": 0, "p": 0, "years": set()})
        node["n"] += 1
        node["p"] += r["p"]
        node["years"].add(r["y"])

    out = []
    for s in SUBJ_ORDER:
        chaps = []
        col = [c for c in CHAPTER_ORDER[s] if c in tree[s]]
        col += [c for c in tree[s] if c not in col]
        for c in col:
            kps = []
            for kid, v in sorted(tree[s][c].items(), key=lambda kv: (-kv[1]["p"], kv[0])):
                kps.append({
                    "id": kid, "name": v["name"], "n": v["n"],
                    "p": v["p"], "ny": len(v["years"]),
                })
            chaps.append({
                "name": c,
                "n": sum(k["n"] for k in kps),
                "p": sum(k["p"] for k in kps),
                "kps": kps,
            })
        chaps.sort(key=lambda c: (-c["p"], c["name"]))
        out.append({
            "key": s,
            "name": SUBJECTS[s],
            "n": sum(c["n"] for c in chaps),
            "p": sum(c["p"] for c in chaps),
            "chapters": chaps,
        })
    return out


TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>408 真题题库索引 · 按考纲知识点检索</title>
<style>
:root{
  --paper:#f6f2e9; --panel:#fcfaf5; --ink:#1a1613; --ink2:#4a423a; --ink3:#8a7f72;
  --rule:#e0d8c9; --rule2:#cfc4b0;
  --DS:#1f5fa8; --CO:#a83226; --OS:#1c6b3c; --NET:#96650a;
  --serif:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",Georgia,serif;
  --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Segoe UI",sans-serif;
  --mono:"Cascadia Mono",Consolas,"Courier New",monospace;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{
  background:var(--paper); color:var(--ink); font-family:var(--sans);
  font-size:14.5px; line-height:1.7;
  background-image:radial-gradient(rgba(160,140,110,.055) 1px,transparent 1px);
  background-size:3px 3px;
}
/* ---------- shell ---------- */
.shell{display:grid;grid-template-columns:306px minmax(0,1fr);min-height:100vh}
aside{
  position:sticky;top:0;height:100vh;overflow-y:auto;background:var(--panel);
  border-right:1px solid var(--rule);padding:22px 0 60px;
}
aside::-webkit-scrollbar{width:8px}
aside::-webkit-scrollbar-thumb{background:var(--rule2);border-radius:4px}
.brand{padding:0 22px 16px;border-bottom:1px solid var(--rule);margin-bottom:14px}
.brand h1{font-family:var(--serif);font-size:19px;margin:0 0 4px;letter-spacing:.5px;font-weight:600}
.brand p{margin:0;font-size:11.5px;color:var(--ink3);letter-spacing:.4px}
.brand .stat{margin-top:10px;font-family:var(--mono);font-size:11px;color:var(--ink2)}
.brand .stat b{color:var(--ink);font-weight:600}

.sb-group{margin:0 0 2px}
.sb-row{
  display:flex;align-items:center;gap:8px;width:100%;border:0;background:none;
  font:inherit;color:var(--ink2);text-align:left;cursor:pointer;
  padding:6px 22px 6px 18px;border-left:2px solid transparent;transition:.14s;
}
.sb-row:hover{background:rgba(0,0,0,.035);color:var(--ink)}
.sb-row.on{background:rgba(0,0,0,.05);color:var(--ink);border-left-color:var(--ac,var(--ink))}
.sb-row .cdot{width:7px;height:7px;border-radius:50%;background:var(--ac,var(--ink3));flex:none}
.sb-row .lbl{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sb-row .num{font-family:var(--mono);font-size:10.5px;color:var(--ink3);flex:none}
.sb-sub{padding-left:34px;font-size:13.2px}
.sb-kp{padding-left:48px;font-size:12.4px;color:var(--ink3)}
.sb-kp .lbl{white-space:normal;line-height:1.45}
.sb-ch{cursor:pointer;user-select:none}
.sb-ch .chev{font-size:9px;color:var(--ink3);transition:transform .18s;flex:none;width:9px}
.sb-ch.open .chev{transform:rotate(90deg)}
.sb-kids{display:none}
.sb-kids.open{display:block;animation:slidedown .18s ease-out}
@keyframes slidedown{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.sb-head{padding:14px 22px 6px;font-size:10.5px;letter-spacing:1.6px;color:var(--ink3);
  text-transform:uppercase;font-family:var(--mono)}

/* ---------- main ---------- */
main{min-width:0;display:flex;flex-direction:column}
.topbar{
  position:sticky;top:0;z-index:20;background:rgba(246,242,233,.94);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--rule);
  padding:12px 30px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;
}
.search{position:relative;flex:1;min-width:220px;max-width:430px}
.search input{
  width:100%;padding:8px 34px 8px 32px;border:1px solid var(--rule2);border-radius:3px;
  background:#fff;font:inherit;font-size:13.5px;color:var(--ink);outline:none;transition:.14s;
}
.search input:focus{border-color:var(--ink2);box-shadow:0 0 0 3px rgba(26,22,19,.06)}
.search .ico{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--ink3);font-size:13px}
.search .kbd{position:absolute;right:8px;top:50%;transform:translateY(-50%);
  font-family:var(--mono);font-size:10px;color:var(--ink3);border:1px solid var(--rule2);
  border-radius:3px;padding:0 4px;background:var(--panel)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{
  border:1px solid var(--rule2);background:#fff;border-radius:999px;
  font:inherit;font-size:12px;padding:4px 12px;cursor:pointer;color:var(--ink2);transition:.14s;
}
.chip:hover{border-color:var(--ink3);color:var(--ink)}
.chip.on{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.chip.ac.on{background:var(--ac);border-color:var(--ac);color:#fff}
.meta{margin-left:auto;font-family:var(--mono);font-size:11.5px;color:var(--ink2);white-space:nowrap}
.meta b{color:var(--ink);font-size:13px}
.btnlink{border:0;background:none;font:inherit;font-size:12px;color:var(--ink3);
  cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.btnlink:hover{color:var(--ink)}

.doc{padding:30px 30px 120px;max-width:1040px}
.crumb{font-size:12px;color:var(--ink3);margin-bottom:6px;font-family:var(--mono);letter-spacing:.3px}
h2.view{font-family:var(--serif);font-size:27px;font-weight:600;margin:0 0 4px;letter-spacing:.6px}
.view-sub{margin:0 0 24px;color:var(--ink2);font-size:13px}

/* year block */
.yearblock{scroll-margin-top:80px;margin-bottom:30px}
.yearhead{
  display:flex;align-items:baseline;gap:12px;padding-bottom:6px;margin-bottom:2px;
  border-bottom:2px solid var(--ink);position:sticky;top:57px;background:var(--paper);z-index:5;
}
.yearhead .yy{font-family:var(--serif);font-size:22px;font-weight:600;letter-spacing:1px}
.yearhead .yc{font-family:var(--mono);font-size:11px;color:var(--ink3)}

/* question row */
.q{
  display:grid;grid-template-columns:46px 1fr 44px;gap:14px;align-items:start;
  padding:11px 4px 11px 0;border-bottom:1px solid var(--rule);
  position:relative;scroll-margin-top:96px;transition:background .12s;
}
.q:before{
  content:"";position:absolute;left:-12px;top:8px;bottom:8px;width:2px;
  background:var(--ac);transform:scaleY(0);transform-origin:top;transition:transform .16s;
}
.q:hover{background:rgba(255,255,255,.7)}
.q:hover:before{transform:scaleY(1)}
.q.flash{animation:flash 1.5s ease-out}
.qwrap.flash{animation:flash 1.6s ease-out}
@keyframes flash{0%{background:rgba(255,214,102,.55)}100%{background:transparent}}
.qno{
  font-family:var(--mono);font-size:13px;color:var(--ink);text-align:right;
  padding-top:1px;letter-spacing:-.5px;
}
.qno span{display:block;font-size:9.5px;color:var(--ink3);letter-spacing:0;margin-top:1px}
.qbody{min-width:0}
.qstem{color:var(--ink);font-size:13.8px;line-height:1.65}
.qtags{display:flex;gap:6px;flex-wrap:wrap;margin-top:5px;align-items:center}
.tag{
  font-size:10.5px;padding:1px 7px;border-radius:2px;letter-spacing:.2px;
  border:1px solid transparent;white-space:nowrap;
}
.tag.kp{background:rgba(0,0,0,.045);color:var(--ink2);cursor:pointer;border-color:var(--rule)}
.tag.kp:hover{background:var(--ac);color:#fff;border-color:var(--ac)}
.tag.ch{background:none;color:var(--ink3);border-color:var(--rule2)}
.tag.sec{background:none;color:var(--ink3);border-color:var(--rule2)}
.tag.type{font-family:var(--mono);background:var(--ink);color:var(--paper);border-color:var(--ink)}
.tag.type.t1{background:var(--ac);border-color:var(--ac);color:#fff}
.qpts{
  font-family:var(--mono);font-size:12px;color:var(--ink2);text-align:right;padding-top:1px;
}
.qpts b{font-size:14px;color:var(--ink)}
/* 解析展开 */
.qwrap{scroll-margin-top:96px}
.qwrap .q{scroll-margin-top:96px}
.tag.ans{background:#e6f4ea;color:#1c6b3c;border-color:#b7dfc4;font-family:var(--mono)}
.tag.nox{background:none;color:#b3a99c;border-color:var(--rule)}
.xbtn{
  border:1px solid var(--rule2);background:#fff;border-radius:2px;font:inherit;
  font-size:10.5px;padding:1px 8px;color:var(--ink2);cursor:pointer;letter-spacing:.2px;
}
.xbtn:hover{border-color:var(--ac,var(--acc));color:var(--ac,var(--acc));background:#fff}
.qexp{
  margin:-2px 0 10px 60px;padding:12px 16px;background:#fffdf8;
  border:1px solid var(--rule);border-left:3px solid var(--ac,var(--acc));border-radius:0 4px 4px 0;
  font-size:13.2px;line-height:1.85;color:var(--ink2);animation:rise .18s ease-out;
}
@keyframes rise{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.qexp .fs{font-family:var(--serif);font-size:13.8px;color:var(--ink);margin-bottom:10px;
  padding-bottom:9px;border-bottom:1px dashed var(--rule)}
.qexp .olist{margin:0 0 10px;padding:0;list-style:none}
.qexp .olist li{padding:3px 0 3px 4px;color:var(--ink)}
.qexp .olist li b{font-family:var(--mono);color:var(--ink3);margin-right:4px}
.qexp .olist li.ok{background:#e6f4ea;border-radius:3px}
.qexp .olist li.ok b{color:var(--ok)}
.qexp .aline{font-family:var(--mono);font-size:12.5px;color:var(--ink2);margin:0 0 8px}
.qexp .aline b{color:var(--ok);font-size:14px}
.qexp .xbody{color:var(--ink2)}
.qexp .xbody b{color:var(--ink)}
.qexp .qimg{margin:0 0 12px;text-align:center;position:relative}
.qexp .qimg img{max-width:100%;height:auto;border:1px solid var(--rule);border-radius:3px;background:#fff}
.qexp .imtag{display:inline-block;margin-top:5px;font-family:var(--mono);font-size:10px;
  color:var(--ink3);letter-spacing:.5px}
@media (max-width:700px){.qexp{margin-left:0}}
.copylink{
  position:absolute;right:0;top:-2px;border:0;background:none;cursor:pointer;
  font-size:11px;color:var(--ink3);opacity:0;transition:.14s;font-family:var(--mono);
}
.q:hover .copylink{opacity:1}
.copylink:hover{color:var(--ink)}

.empty{padding:60px 0;text-align:center;color:var(--ink3);font-size:13px}
.empty b{display:block;font-family:var(--serif);font-size:19px;color:var(--ink2);margin-bottom:6px}

footer.docfoot{margin-top:44px;padding-top:16px;border-top:1px solid var(--rule);
  font-size:11.5px;color:var(--ink3);font-family:var(--mono)}

/* mobile */
.menubtn{display:none}
@media (max-width:900px){
  .shell{grid-template-columns:1fr}
  aside{position:fixed;left:0;top:0;z-index:60;width:290px;transform:translateX(-100%);
    transition:transform .22s;box-shadow:0 0 40px rgba(0,0,0,.18)}
  aside.open{transform:none}
  .menubtn{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--rule2);
    background:#fff;border-radius:3px;padding:6px 10px;font:inherit;font-size:12.5px;cursor:pointer}
  .doc{padding:20px 16px 100px}
  .topbar{padding:10px 14px}
  .q{grid-template-columns:36px 1fr 40px;gap:10px}
  .yearhead{top:52px}
}
@media print{
  aside,.topbar,.copylink{display:none!important}
  .shell{grid-template-columns:1fr}
  .doc{max-width:none;padding:0}
  body{background:#fff}
}

.rt p.para{margin:0 0 8px}
.rt p.para:last-child{margin-bottom:0}
.rt pre.code{margin:8px 0 12px;padding:10px 12px;background:#f7f4ec;border:1px solid var(--rule);
  border-left:3px solid var(--ac,#8a7f72);border-radius:3px;overflow-x:auto;
  font-family:var(--mono);font-size:12.4px;line-height:1.62;white-space:pre;color:#2b2622;
  -webkit-text-size-adjust:100%}
.rt{word-break:break-word}
</style>
</head>
<body>
<div class="shell">
  <aside id="sb">
    <div class="brand">
      <h1>408 真题题库索引</h1>
      <p>按考纲知识点检索 · 2009–2026</p>
      <div class="stat"><b id="totQ">0</b> 题 · <b id="totP">0</b> 分 · <b id="totY">0</b> 套卷</div>
    </div>
    <div class="sb-head">范围</div>
    <button class="sb-row on" data-nav="all" style="--ac:#1a1613">
      <span class="cdot"></span><span class="lbl">全部题目</span><span class="num" id="navAllN"></span>
    </button>
    <div class="sb-head">按科目 / 章 / 知识点</div>
    <div id="tree"></div>
  </aside>

  <main>
    <div class="topbar">
      <button class="menubtn" id="menuBtn">☰ 目录</button>
      <div class="search">
        <span class="ico">⌕</span>
        <input id="q" type="search" placeholder="搜索题干、知识点、章节…">
        <span class="kbd">/</span>
      </div>
      <div class="chips" id="typeChips">
        <button class="chip on" data-type="all">全部题型</button>
        <button class="chip" data-type="0">选择题</button>
        <button class="chip" data-type="1">综合题</button>
      </div>
      <button class="btnlink" id="reset">重置</button>
      <a class="btnlink" href="map.html" style="text-decoration:none">知识体系</a>
      <a class="btnlink" href="quiz.html" style="text-decoration:none">刷选择</a>
      <a class="btnlink" href="bigq.html" style="text-decoration:none">刷大题</a>
      <div class="meta"><b id="hitN">0</b> 题 / <b id="hitP">0</b> 分</div>
    </div>

    <div class="doc">
      <div class="crumb" id="crumb">INDEX / ALL</div>
      <h2 class="view" id="viewTitle">全部题目</h2>
      <p class="view-sub" id="viewSub"></p>
      <div id="list"></div>
      <footer class="docfoot">
        DATA · questions_classified.csv &nbsp;|&nbsp;
        <a href="quiz.html">刷题 →</a> &nbsp;|&nbsp; <a href="index.html">← 返回完整分析报告</a>
      </footer>
    </div>
  </main>
</div>

<script id="payload" type="application/json">__DATA__</script>
<script>
(function(){
  const P = JSON.parse(document.getElementById('payload').textContent);
  const ROWS = P.rows, TREE = P.tree;
  const SUBJ = {DS:'数据结构',CO:'计算机组成原理',OS:'操作系统',NET:'计算机网络'};
  const ACC  = {DS:'#1f5fa8',CO:'#a83226',OS:'#1c6b3c',NET:'#96650a'};

  const state = {scope:'all', kp:null, ch:null, subj:null, type:'all', text:''};
  const $ = s => document.querySelector(s);
  const el = (t,c,h)=>{const e=document.createElement(t); if(c)e.className=c; if(h!=null)e.innerHTML=h; return e;};

  /* ---------- totals ---------- */
  const totQ = ROWS.length, totP = ROWS.reduce((a,r)=>a+r.p,0);
  const years = [...new Set(ROWS.map(r=>r.y))].sort();
  $('#totQ').textContent = totQ;
  $('#totP').textContent = totP;
  $('#totY').textContent = years.length;
  $('#navAllN').textContent = totQ;

  /* ---------- sidebar tree ---------- */
  const treeBox = $('#tree');
  TREE.forEach(sb=>{
    const group = el('div','sb-group');
    const row = el('button','sb-row sb-ch open','<span class="chev">▶</span><span class="cdot"></span>'+
      '<span class="lbl">'+sb.name+'</span><span class="num">'+sb.n+'</span>');
    row.style.setProperty('--ac', ACC[sb.key]);
    row.dataset.subj = sb.key;
    const kids = el('div','sb-kids open');
    sb.chapters.forEach(ch=>{
      const crow = el('button','sb-row sb-ch sb-sub',
        '<span class="chev">▶</span><span class="lbl">'+esc(ch.name)+'</span><span class="num">'+ch.n+'</span>');
      crow.style.setProperty('--ac', ACC[sb.key]);
      const ckids = el('div','sb-kids');
      ch.kps.forEach(kp=>{
        const krow = el('button','sb-row sb-kp',
          '<span class="lbl">'+esc(kp.name)+'</span><span class="num">'+kp.n+'</span>');
        krow.style.setProperty('--ac', ACC[sb.key]);
        krow.dataset.kp = kp.id;
        krow.dataset.subj = sb.key;
        krow.dataset.ch = ch.name;
        krow.onclick = e => { e.stopPropagation(); go({scope:'kp',kp:kp.id,subj:sb.key,ch:ch.name}); };
        ckids.appendChild(krow);
      });
      crow.dataset.subj = sb.key;
      crow.dataset.ch = ch.name;
      crow.onclick = e => {
        e.stopPropagation();
        const open = crow.classList.toggle('open');
        ckids.classList.toggle('open', open);
        go({scope:'ch',subj:sb.key,ch:ch.name});
      };
      kids.appendChild(crow); kids.appendChild(ckids);
    });
    row.onclick = e=>{
      e.stopPropagation();
      const open = row.classList.toggle('open');
      kids.classList.toggle('open', open);
      go({scope:'subj',subj:sb.key});
    };
    group.appendChild(row); group.appendChild(kids);
    treeBox.appendChild(group);
  });

  document.querySelector('[data-nav="all"]').onclick = ()=>go({scope:'all'});

  /* ---------- chips ---------- */
  document.querySelectorAll('#typeChips .chip').forEach(c=>{
    c.onclick = ()=>{
      document.querySelectorAll('#typeChips .chip').forEach(x=>x.classList.remove('on'));
      c.classList.add('on');
      state.type = c.dataset.type;
      render();
    };
  });
  $('#reset').onclick = ()=>{ $('#q').value=''; go({scope:'all'}); };

  /* ---------- search ---------- */
  let timer;
  $('#q').addEventListener('input', e=>{
    clearTimeout(timer);
    timer = setTimeout(()=>{ state.text = e.target.value.trim().toLowerCase(); render(); }, 120);
  });
  document.addEventListener('keydown', e=>{
    if(e.key==='/' && document.activeElement!==$('#q')){ e.preventDefault(); $('#q').focus(); }
    if(e.key==='Escape'){ $('#q').value=''; state.text=''; render(); }
  });

  /* ---------- navigation ---------- */
  function go(next){
    state.scope = next.scope;
    state.kp = next.kp||null; state.ch = next.ch||null; state.subj = next.subj||null;
    syncHash();
    syncSidebar();
    render();
    if(window.innerWidth<=900) $('#sb').classList.remove('open');
    window.scrollTo({top:0,behavior:'smooth'});
  }
  function syncHash(){
    let h = '#';
    if(state.scope==='kp') h += 'kp='+encodeURIComponent(state.kp);
    else if(state.scope==='ch') h += 'ch='+encodeURIComponent(state.subj+'/'+state.ch);
    else if(state.scope==='subj') h += 'subj='+state.subj;
    else h += 'all';
    history.replaceState(null,'',h);
  }
  function syncSidebar(){
    document.querySelectorAll('.sb-row').forEach(r=>r.classList.remove('on'));
    if(state.scope==='all'){ document.querySelector('[data-nav="all"]').classList.add('on'); return; }
    let sel=null;
    if(state.scope==='kp') sel = document.querySelector('.sb-kp[data-kp="'+CSS.escape(state.kp)+'"]');
    else if(state.scope==='ch') sel = document.querySelector('.sb-ch[data-ch="'+CSS.escape(state.ch)+'"][data-subj="'+state.subj+'"]');
    else if(state.scope==='subj') sel = document.querySelector('.sb-ch[data-subj="'+state.subj+'"]:not(.sb-sub)');
    if(sel){ sel.classList.add('on'); }
  }

  /* ---------- filter + render ---------- */
  function filtered(){
    return ROWS.filter(r=>{
      if(state.scope==='kp' && r.kp!==state.kp) return false;
      if(state.scope==='ch' && !(r.s===state.subj && r.ch===state.ch)) return false;
      if(state.scope==='subj' && r.s!==state.subj) return false;
      if(state.type!=='all' && String(r.t)!==state.type) return false;
      if(state.text){
        const hay = (r.st+' '+r.kn+' '+r.ch+' '+r.sec+' '+r.y+' '+r.q).toLowerCase();
        if(!hay.includes(state.text)) return false;
      }
      return true;
    });
  }

  function render(){
    const rows = filtered();
    const pts = rows.reduce((a,r)=>a+r.p,0);
    $('#hitN').textContent = rows.length;
    $('#hitP').textContent = pts;

    let t='全部题目', sub='', crumb='INDEX / ALL';
    if(state.scope==='kp'){
      const m = rows[0];
      t = m ? m.kn : state.kp;
      crumb = 'INDEX / '+state.subj+' / '+state.ch;
      sub = '知识点 '+state.kp+' · 所在章：'+state.ch;
    } else if(state.scope==='ch'){
      t = state.ch; crumb='INDEX / '+state.subj; sub = SUBJ[state.subj]+' · 本章收录';
    } else if(state.scope==='subj'){
      t = SUBJ[state.subj]; crumb='INDEX / '+state.subj; sub='本科目全部题目';
    } else {
      sub = '共 '+totQ+' 题；点击左侧目录可按科目 / 章 / 知识点下钻';
    }
    $('#viewTitle').textContent = t;
    $('#crumb').textContent = crumb;
    $('#viewSub').textContent = sub + ' · 命中 ' + rows.length + ' 题 / ' + pts + ' 分';

    const list = $('#list');
    list.innerHTML='';
    if(!rows.length){
      list.appendChild(el('div','empty','<b>没有匹配的题目</b>换个关键词，或点「重置」'));
      return;
    }
    const byYear = {};
    rows.forEach(r=>{ (byYear[r.y] = byYear[r.y]||[]).push(r); });
    Object.keys(byYear).sort().forEach((y,gi)=>{
      const block = el('section','yearblock');
      block.id = 'y-'+y;
      const ys = byYear[y];
      block.appendChild(el('div','yearhead',
        '<span class="yy">'+y+'</span><span class="yc">'+ys.length+' 题 · '+
        ys.reduce((a,r)=>a+r.p,0)+' 分</span>'));
      ys.forEach((r,i)=>{
        const wrap = el('div','qwrap');
        wrap.id = 'q-'+r.y+'-'+r.q;
        const row = el('div','q');
        row.style.setProperty('--ac', ACC[r.s]);
        const typeLbl = r.t ? '综合' : '选择';
        const hasX = !!(r.x || r.o);
        row.innerHTML =
          '<div class="qno">'+r.q+'<span>'+r.y+'</span></div>'+
          '<div class="qbody">'+
            '<div class="qstem">'+esc(r.st)+'</div>'+
            '<div class="qtags">'+
              '<span class="tag type '+(r.t?'t1':'')+'">'+typeLbl+'</span>'+
              '<span class="tag ch">'+esc(r.ch)+'</span>'+
              '<span class="tag kp" data-kp="'+r.kp+'">'+esc(r.kn)+'</span>'+
              (r.a?'<span class="tag ans">答案 '+r.a+'</span>':'')+
              (hasX?'<button class="xbtn">▾ 解析</button>'
                   :'<span class="tag nox">暂无解析</span>')+
            '</div>'+
          '</div>'+
          '<div class="qpts"><b>'+r.p+'</b>分</div>'+
          '<button class="copylink" title="复制直达链接">#link</button>';
        row.querySelector('.copylink').onclick = ev=>{
          ev.stopPropagation();
          const url = location.href.split('#')[0]+'#q='+r.y+'-'+r.q;
          const done = ()=>{ ev.target.textContent='copied';
                             setTimeout(()=>ev.target.textContent='#link',1200); };
          try{
            if(navigator.clipboard && navigator.clipboard.writeText){
              navigator.clipboard.writeText(url).then(done).catch(()=>prompt('复制链接：',url));
            } else { prompt('复制链接：',url); }
          }catch(e){ prompt('复制链接：',url); }
        };
        row.querySelector('.tag.kp').onclick = ev=>{
          ev.stopPropagation();
          go({scope:'kp', kp:r.kp, subj:r.s, ch:r.ch});
        };
        row.querySelector('.tag.ch').onclick = ev=>{
          ev.stopPropagation();
          go({scope:'ch', subj:r.s, ch:r.ch});
        };
        const xb = row.querySelector('.xbtn');
        if(xb){
          const exp = el('div','qexp');
          exp.hidden = true;
          const parts = [];
          if(r.im) parts.push('<div class="qimg">'+
            '<img loading="lazy" src="'+r.im+'" alt="本题插图">'+
            (r.imscan?'<span class="imtag">原卷截图</span>':'')+'</div>');
          if(r.t===1 && r.fs) parts.push('<div class="fs rt">'+richText(r.fs)+'</div>');
          if(r.o) parts.push('<ol class="olist">'+
            r.o.map((o,k)=>'<li class="'+(r.a && 'ABCD'[k]===r.a?'ok':'')+'">'+
              '<b>'+'ABCD'[k]+'.</b> '+esc(o)+'</li>').join('')+'</ol>');
          if(r.a) parts.push('<div class="aline">正确答案：<b>'+r.a+'</b></div>');
          if(r.x) parts.push('<div class="xbody rt"><b>'+(r.t===1?'参考答案与思路：':'解析：')+
            '</b>'+richText(r.x)+'</div>');
          exp.innerHTML = parts.join('');
          xb.onclick = ev=>{
            ev.stopPropagation();
            exp.hidden = !exp.hidden;
            xb.textContent = exp.hidden ? '▾ 解析' : '▴ 收起';
          };
          wrap.appendChild(row); wrap.appendChild(exp);
        } else {
          wrap.appendChild(row);
        }
        block.appendChild(wrap);
      });
      list.appendChild(block);
    });
  }

  function esc(s){ return String(s).replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

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

  /* ---------- deep link on load ---------- */
  function fromHash(){
    const h = decodeURIComponent(location.hash.slice(1));
    if(!h || h==='all'){ go({scope:'all'}); return; }
    const mQ = h.match(/^q=(\d{4})-(\d+)$/);
    const mK = h.match(/^kp=(.+)$/);
    const mC = h.match(/^ch=([^/]+)\/(.+)$/);
    const mS = h.match(/^subj=(.+)$/);
    if(mQ){
      const y=mQ[1], q=mQ[2];
      const row = ROWS.find(r=>String(r.y)===y && String(r.q)===q);
      if(row){ state.type='all'; state.text=''; go({scope:'all'}); }
      setTimeout(()=>{
        const node = document.getElementById('q-'+y+'-'+q);
        if(node){ node.scrollIntoView({block:'center',behavior:'smooth'});
          node.classList.add('flash'); setTimeout(()=>node.classList.remove('flash'),1600); }
      },60);
      return;
    }
    if(mK){ const r = ROWS.find(x=>x.kp===mK[1]); go({scope:'kp',kp:mK[1],subj:r?r.s:null,ch:r?r.ch:null}); return; }
    if(mC){ go({scope:'ch',subj:mC[1],ch:mC[2]}); return; }
    if(mS){ go({scope:'subj',subj:mS[1]}); return; }
    go({scope:'all'});
  }

  $('#menuBtn').onclick = ()=> $('#sb').classList.toggle('open');
  window.addEventListener('hashchange', fromHash);

  render();
  fromHash();
})();
</script>
</body>
</html>
"""


def main():
    rows = load_rows()
    tree = build_tree(rows)
    payload = json.dumps({"rows": rows, "tree": tree}, ensure_ascii=False, separators=(",", ":"))
    # 防止题干里出现 </script> 或 < 破坏 HTML 解析
    payload = (payload.replace("<", "\\u003c")
                      .replace(">", "\\u003e")
                      .replace("&", "\\u0026"))
    html = TEMPLATE.replace("__DATA__", payload)
    dest = os.path.join(OUT, "browse.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {dest}  {len(html)/1024:.0f} K chars (={len(html.encode('utf-8'))/1024:.0f} KB)"
          f"  rows={len(rows)}  subjects={len(tree)}  "
          f"chapters={sum(len(t['chapters']) for t in tree)}")


if __name__ == "__main__":
    main()


