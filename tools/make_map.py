# -*- coding: utf-8 -*-
"""Build out/map.html — the interactive knowledge framework.

思维导图的 HTML 版本：四科 → 章 → 知识点，每行都带「刷选择 / 刷大题 / 看题」入口，
把"知识框架"和"题库"直接连起来。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syllabus import SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")

CHAPTER_ORDER = {
    "DS": ["绪论", "线性表", "栈、队列和数组", "串", "树与二叉树", "图", "查找", "排序"],
    "CO": ["计算机系统概述", "数据的表示和运算", "存储器层次结构", "指令系统",
           "中央处理器", "总线与输入输出"],
    "OS": ["操作系统概述", "进程管理", "内存管理", "文件管理", "输入输出管理"],
    "NET": ["计算机网络概述", "物理层", "数据链路层", "网络层", "传输层", "应用层"],
}
CHAPTER_TITLE = {
    "绪论": "第一章 绪论", "线性表": "第二章 线性表", "栈、队列和数组": "第三章 栈、队列和数组",
    "串": "第四章 串", "树与二叉树": "第五章 树与二叉树", "图": "第六章 图",
    "查找": "第七章 查找", "排序": "第八章 排序",
    "计算机系统概述": "第一章 系统概述", "数据的表示和运算": "第二章 数据表示与运算",
    "存储器层次结构": "第三章 存储器层次结构", "指令系统": "第四章 指令系统",
    "中央处理器": "第五章 中央处理器", "总线与输入输出": "第六章 总线与 I/O",
    "操作系统概述": "第一章 概述", "进程管理": "第二章 进程管理", "内存管理": "第三章 内存管理",
    "文件管理": "第四章 文件管理", "输入输出管理": "第五章 I/O 管理",
    "计算机网络概述": "第一章 网络概述", "物理层": "第二章 物理层",
    "数据链路层": "第三章 数据链路层", "网络层": "第四章 网络层",
    "传输层": "第五章 传输层", "应用层": "第六章 应用层",
}

TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>408 知识体系 · 可点进题库</title>
<style>
:root{
  --paper:#f6f2e9;--panel:#fcfaf5;--ink:#1a1613;--ink2:#4a423a;--ink3:#8a7f72;
  --rule:#e0d8c9;--rule2:#cfc4b0;--acc:#1f5fa8;
  --DS:#1f5fa8;--CO:#a83226;--OS:#1c6b3c;--NET:#96650a;
  --serif:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",Georgia,serif;
  --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Segoe UI",sans-serif;
  --mono:"Cascadia Mono",Consolas,"Courier New",monospace;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:14.5px;line-height:1.7;
  background-image:radial-gradient(rgba(160,140,110,.055) 1px,transparent 1px);background-size:3px 3px;}
.bar{position:sticky;top:0;z-index:20;background:rgba(246,242,233,.95);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--rule);padding:10px 20px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.bar .ttl{font-family:var(--serif);font-size:16px;font-weight:600;letter-spacing:.4px}
.bar .right{margin-left:auto;display:flex;gap:8px}
.bar a{border:1px solid var(--rule2);background:#fff;border-radius:3px;font-size:12px;
  padding:4px 9px;color:var(--ink2);text-decoration:none}
.bar a:hover{border-color:var(--ink3);color:var(--ink)}
.bar a.primary{background:var(--ink);border-color:var(--ink);color:var(--paper)}
main{max-width:980px;margin:0 auto;padding:30px 20px 110px}
h1{font-family:var(--serif);font-size:29px;font-weight:600;letter-spacing:.8px;margin:2px 0 4px}
.lede{color:var(--ink2);font-size:13.4px;margin:0 0 8px}
.legend{font-size:11.8px;color:var(--ink3);font-family:var(--mono);margin:0 0 22px}
.legend b{color:var(--ink)}

.subj{margin:0 0 30px;border-left:3px solid var(--ac);padding-left:0}
.subjhead{display:flex;align-items:baseline;gap:12px;padding:0 0 7px 14px;
  border-bottom:2px solid var(--ac);margin-bottom:2px;flex-wrap:wrap}
.subjhead h2{font-family:var(--serif);font-size:21px;font-weight:600;margin:0;color:var(--ac);
  letter-spacing:.6px}
.subjhead .m{font-family:var(--mono);font-size:11.5px;color:var(--ink3)}
.subjhead .acts{margin-left:auto;display:flex;gap:6px}
.mini{border:1px solid var(--rule2);background:#fff;border-radius:2px;font:inherit;
  font-size:11.5px;padding:3px 8px;color:var(--ink2);cursor:pointer;text-decoration:none}
.mini:hover{border-color:var(--ac);color:var(--ac)}
.mini.solid{background:var(--ac);border-color:var(--ac);color:#fff}
.mini.solid:hover{filter:brightness(1.1);color:#fff}

.chap{padding:10px 0 4px 14px}
.chaphead{display:flex;align-items:center;gap:10px;margin-bottom:4px;flex-wrap:wrap}
.chaphead h3{font-family:var(--serif);font-size:15.5px;font-weight:600;margin:0;letter-spacing:.3px}
.chaphead .m{font-family:var(--mono);font-size:11px;color:var(--ink3)}
.chaphead .acts{margin-left:auto;display:flex;gap:5px}

.kp{display:grid;grid-template-columns:1fr auto auto;gap:10px;align-items:center;
  padding:5px 8px 5px 20px;border-bottom:1px solid var(--rule);position:relative}
.kp:before{content:"";position:absolute;left:8px;top:50%;width:7px;height:1px;background:var(--rule2)}
.kp:hover{background:rgba(255,255,255,.75)}
.kp .name{font-size:13.3px;color:var(--ink);min-width:0}
.kp .name .hot{font-family:var(--mono);font-size:10px;padding:0 4px;border-radius:2px;
  margin-right:6px;vertical-align:1px}
.hot.must{background:#fff3e0;color:#96590a;border:1px solid #f0d3a8}
.hot.high{background:#eef3fb;color:#1f5fa8;border:1px solid #b9d2f5}
.kp .cnt{font-family:var(--mono);font-size:11px;color:var(--ink3);white-space:nowrap}
.kp .acts{display:flex;gap:4px;opacity:.55;transition:.13s}
.kp:hover .acts{opacity:1}
.kp .acts a{font-size:11px;padding:2px 7px;border:1px solid var(--rule2);border-radius:2px;
  background:#fff;color:var(--ink2);text-decoration:none;white-space:nowrap}
.kp .acts a:hover{background:var(--ac);border-color:var(--ac);color:#fff}
.kp .acts a.dis{opacity:.35;pointer-events:none}
.foot{margin-top:34px;padding-top:14px;border-top:1px solid var(--rule);
  font-size:11.5px;color:var(--ink3);font-family:var(--mono)}
@media (max-width:700px){
  main{padding:16px 12px 90px}
  .kp{grid-template-columns:1fr auto;grid-template-areas:"n c" "a a";row-gap:4px}
  .kp .acts{grid-area:a;opacity:1;flex-wrap:wrap}
  .kp .name{grid-area:n}.kp .cnt{grid-area:c}
  .subjhead .acts{margin-left:0}
  .chaphead .acts{margin-left:0}
}
@media print{.bar,.acts{display:none}}
</style>
</head>
<body>
<div class="bar">
  <span class="ttl">408 知识体系</span>
  <span class="right">
    <a href="index.html">入口</a>
    <a href="browse.html">题库</a>
    <a class="primary" href="quiz.html">刷选择题</a>
    <a class="primary" href="bigq.html">刷大题</a>
  </span>
</div>
<main>
  <h1>知识体系 → 题库</h1>
  <p class="lede">四科 → 章 → 知识点。每个知识点右侧可直接跳进对应题库：<b>刷选择</b>（有答案，即时判分）
    或 <b>刷大题</b>（综合题，可看参考答案与思路）。</p>
  <p class="legend">【必】= 18 年中 <b>≥14 年</b>考到　【高】= <b>10–13 年</b>　
    数字 = 该知识点选择题 / 综合题数量</p>
  <div id="tree"></div>
  <div class="foot">数据来自本地 18 套真题 + 各年官方解析 · 选择题 686 道 / 综合题 119 道</div>
</main>
<script id="payload" type="application/json">__DATA__</script>
<script>
(function(){
  const D = JSON.parse(document.getElementById('payload').textContent);
  const S = D.subjects, ACC = {DS:'#1f5fa8',CO:'#a83226',OS:'#1c6b3c',NET:'#96650a'};
  const box = document.getElementById('tree');
  const esc = s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

  S.forEach(sb=>{
    const sec = document.createElement('section');
    sec.className = 'subj';
    sec.style.setProperty('--ac', ACC[sb.key]);
    sec.innerHTML = `
      <div class="subjhead">
        <h2>${esc(sb.name)}</h2>
        <span class="m">选择 ${sb.sel} · 综合 ${sb.big} · 年均 ${sb.avg} 分</span>
        <span class="acts">
          <a class="mini solid" href="quiz.html?subj=${sb.key}">刷本科选择题</a>
          <a class="mini" href="browse.html#subj=${sb.key}">看全部题</a>
        </span>
      </div>` +
      sb.chapters.map(ch=>`
        <div class="chap">
          <div class="chaphead">
            <h3>${esc(ch.title)}</h3>
            <span class="m">选择 ${ch.sel} · 综合 ${ch.big} · 年均 ${ch.avg} 分</span>
            <span class="acts">
              <a class="mini solid" href="quiz.html?chap=${encodeURIComponent(sb.key+'|'+ch.name)}">刷本章</a>
              <a class="mini" href="bigq.html?chap=${encodeURIComponent(sb.key+'|'+ch.name)}">刷本章大题</a>
            </span>
          </div>` +
          ch.kps.map(k=>{
            const hot = k.ny>=14 ? '<span class="hot must">必</span>'
                      : (k.ny>=10 ? '<span class="hot high">高</span>' : '');
            const selDis = k.sel ? '' : ' dis';
            const bigDis = k.big ? '' : ' dis';
            return `<div class="kp">
              <span class="name">${hot}${esc(k.name)}</span>
              <span class="cnt">${k.sel} / ${k.big}</span>
              <span class="acts">
                <a class="${selDis.trim()}" href="quiz.html?kp=${encodeURIComponent(k.id)}">刷选择</a>
                <a class="${bigDis.trim()}" href="bigq.html?kp=${encodeURIComponent(k.id)}">刷大题</a>
                <a href="browse.html#kp=${encodeURIComponent(k.id)}">看题</a>
              </span></div>`;
          }).join('') +
        `</div>`).join('');
    box.appendChild(sec);
  });
})();
</script>
</body>
</html>
"""


def main():
    summary = json.load(open(os.path.join(OUT, "data", "summary.json"), encoding="utf-8"))
    quiz = json.load(open(os.path.join(OUT, "data", "quiz.json"), encoding="utf-8"))
    bp = os.path.join(OUT, "data", "bigq.json")
    bigq = json.load(open(bp, encoding="utf-8")) if os.path.exists(bp) else []
    ny = len(summary["years"])

    sel_by_kp, big_by_kp = {}, {}
    for r in quiz:
        sel_by_kp[r["kp"]] = sel_by_kp.get(r["kp"], 0) + 1
    for r in bigq:
        big_by_kp[r["kp"]] = big_by_kp.get(r["kp"], 0) + 1

    kp_meta = {k["id"]: k for k in summary["kps"]}
    chap_pts = {(c["subject"], c["chapter"]): c["points"] for c in summary["chapters"]}

    subjects = []
    for key in ["DS", "CO", "OS", "NET"]:
        chaps = []
        names = [c for c in CHAPTER_ORDER[key]
                 if any(k["chapter"] == c for k in summary["kps"] if k["subject"] == key)]
        names += [c["chapter"] for c in summary["chapters"]
                  if c["subject"] == key and c["chapter"] not in names]
        for cn in names:
            ks = [k for k in summary["kps"] if k["subject"] == key and k["chapter"] == cn]
            ks.sort(key=lambda k: (-k["n_years"], -k["points"], k["id"]))
            if not ks:
                continue
            chaps.append({
                "name": cn,
                "title": CHAPTER_TITLE.get(cn, cn),
                "sel": sum(sel_by_kp.get(k["id"], 0) for k in ks),
                "big": sum(big_by_kp.get(k["id"], 0) for k in ks),
                "avg": round(chap_pts.get((key, cn), 0) / ny, 1),
                "kps": [{"id": k["id"], "name": k["name"], "ny": k["n_years"],
                         "sel": sel_by_kp.get(k["id"], 0),
                         "big": big_by_kp.get(k["id"], 0)} for k in ks],
            })
        subjects.append({
            "key": key, "name": SUBJECTS[key],
            "sel": sum(c["sel"] for c in chaps),
            "big": sum(c["big"] for c in chaps),
            "avg": round(sum(c["avg"] for c in chaps), 1),
            "chapters": chaps,
        })

    payload = json.dumps({"subjects": subjects}, ensure_ascii=False,
                         separators=(",", ":")).replace("<", "\\u003c")
    html = TEMPLATE.replace("__DATA__", payload)
    dest = os.path.join(OUT, "map.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    n_kp = sum(len(c["kps"]) for s in subjects for c in s["chapters"])
    print(f"wrote {dest}  {len(html.encode('utf-8'))/1024:.0f} KB  "
          f"subjects={len(subjects)} chapters={sum(len(s['chapters']) for s in subjects)} "
          f"kps={n_kp}")


if __name__ == "__main__":
    main()
