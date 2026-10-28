# -*- coding: utf-8 -*-
"""Build out/quiz.html — a graded 408 multiple-choice drill with selectable banks.

题库维度：全部 / 专题 / 科目 / 章节 / 知识点 / 年份 / 考频 / 错题本
刷题格式：乱序·按年份 ; 即时判分·交卷判分 ; 题量 10/20/50/全部
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syllabus import SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")

# ---------------------------------------------------------------- 预设专题库
TOPICS = [
    ("cache", "Cache 与存储层次", "命中率/映射方式/写策略/页表 TLB —— 全卷分值最高的一块",
     ["CO.3.5", "CO.3.6", "CO.3.7", "OS.3.2", "OS.3.3", "OS.3.4"]),
    ("pipe", "指令流水线", "冒险判定、时空图、加速比与吞吐率",
     ["CO.5.5"]),
    ("pv", "PV 同步与死锁", "信号量建模、经典同步问题、银行家算法",
     ["OS.2.5", "OS.2.6", "OS.2.7", "OS.2.9"]),
    ("netcalc", "子网与网络计算", "CIDR/子网掩码、TCP 窗口与拥塞、时延带宽",
     ["NET.4.3", "NET.4.4", "NET.5.4", "NET.5.5", "NET.1.1"]),
    ("treegraph", "树与图算法", "遍历还原、哈夫曼、MST、最短路、拓扑与关键路径",
     ["DS.5.1", "DS.5.3", "DS.5.6", "DS.5.8", "DS.5.9", "DS.6.1", "DS.6.4",
      "DS.6.5", "DS.6.6", "DS.6.7"]),
    ("sortsearch", "排序与查找", "各排序算法性质、折半/散列/B 树、ASL 计算",
     ["DS.7.1", "DS.7.3", "DS.7.4", "DS.7.6", "DS.8.1", "DS.8.4", "DS.8.6", "DS.8.8"]),
    ("datarep", "数据表示与运算", "补码/IEEE754/溢出标志/大小端对齐",
     ["CO.2.1", "CO.2.2", "CO.2.4", "CO.2.6"]),
    ("cpuio", "CPU 与 I/O", "指令执行、数据通路、中断异常、DMA 与总线",
     ["CO.5.1", "CO.5.2", "CO.5.3", "CO.5.4", "CO.6.1", "CO.6.3", "CO.6.4"]),
    ("memfile", "内存与文件系统", "页面置换、虚拟内存、索引结点与空闲空间管理",
     ["OS.3.3", "OS.3.4", "OS.4.1", "OS.4.3", "OS.4.5", "OS.5.3"]),
    ("protolayer", "协议与分层细节", "TCP/UDP、以太网与 VLAN、路由与 DHCP/ARP/ICMP",
     ["NET.1.2", "NET.3.4", "NET.3.5", "NET.4.2", "NET.4.5", "NET.5.1", "NET.5.3"]),
]

TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>408 刷题 · 单选题训练</title>
<style>
:root{
  --paper:#f6f2e9;--panel:#fcfaf5;--ink:#1a1613;--ink2:#4a423a;--ink3:#8a7f72;
  --rule:#e0d8c9;--rule2:#cfc4b0;--acc:#1f5fa8;
  --ok:#1c6b3c;--okbg:#e6f4ea;--bad:#a83226;--badbg:#fbe9e7;--sel:#1f5fa8;--selbg:#e8f0fb;
  --DS:#1f5fa8;--CO:#a83226;--OS:#1c6b3c;--NET:#96650a;
  --serif:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",Georgia,serif;
  --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Segoe UI",sans-serif;
  --mono:"Cascadia Mono",Consolas,"Courier New",monospace;
}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%}
body{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.75;
  background-image:radial-gradient(rgba(160,140,110,.055) 1px,transparent 1px);background-size:3px 3px;}
.bar{position:sticky;top:0;z-index:20;background:rgba(246,242,233,.95);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--rule);padding:10px 20px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.bar .ttl{font-family:var(--serif);font-size:16px;font-weight:600;letter-spacing:.4px}
.bar .prog{font-family:var(--mono);font-size:11.5px;color:var(--ink3)}
.bar .score{font-family:var(--mono);font-size:12px;color:var(--ink2)}
.bar .score b{color:var(--ink)}
.bar .right{margin-left:auto;display:flex;gap:8px;align-items:center}
.bar a,.bar button.lnk{border:1px solid var(--rule2);background:#fff;border-radius:3px;
  font:inherit;font-size:12px;padding:4px 9px;color:var(--ink2);cursor:pointer;text-decoration:none}
.bar a:hover,.bar button.lnk:hover{border-color:var(--ink3);color:var(--ink)}
.pbar{height:3px;background:var(--rule);position:sticky;top:51px;z-index:19}
.pbar i{display:block;height:100%;background:var(--acc);width:0;transition:width .25s}
main{max-width:860px;margin:0 auto;padding:30px 20px 120px}

/* ---------- 题库选择 ---------- */
h1{font-family:var(--serif);font-size:29px;font-weight:600;letter-spacing:.8px;margin:4px 0 4px}
.lede{color:var(--ink2);font-size:13.4px;margin:0 0 20px}
.step{margin:0 0 18px}
.step>label{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:10.5px;
  letter-spacing:1.8px;color:var(--ink3);text-transform:uppercase;margin-bottom:7px}
.step>label i{width:15px;height:15px;border:1px solid var(--rule2);border-radius:50%;
  display:grid;place-items:center;font-style:normal;font-size:9px;color:var(--ink3)}
.seg{display:flex;flex-wrap:wrap;gap:5px}
.seg button{border:1px solid var(--rule2);background:#fff;border-radius:3px;font:inherit;
  font-size:13px;padding:6px 12px;cursor:pointer;color:var(--ink2);transition:.13s;white-space:nowrap}
.seg button:hover{border-color:var(--ink3);color:var(--ink)}
.seg button.on{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.panel{margin:10px 0 0;padding:12px;background:#fff;border:1px solid var(--rule);border-radius:5px}
.rows{display:flex;flex-wrap:wrap;gap:6px;max-height:250px;overflow:auto}
.rows button{border:1px solid var(--rule);background:#fff;border-radius:2px;font:inherit;
  font-size:12.5px;padding:4px 9px;cursor:pointer;color:var(--ink2);text-align:left;transition:.12s}
.rows button small{font-family:var(--mono);font-size:10px;color:var(--ink3);margin-left:5px}
.rows button:hover{border-color:var(--ink3);color:var(--ink)}
.rows button.on{background:#e9eff7;border-color:var(--acc);color:var(--ink);font-weight:600}
.crumbline{font-size:12px;color:var(--ink3);margin:8px 0 0;font-family:var(--mono)}
.crumbline b{color:var(--ink);font-weight:600}
.go{margin-top:22px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;
  padding-top:18px;border-top:1px solid var(--rule)}
.btn{background:var(--ink);color:var(--paper);border:0;border-radius:3px;font:inherit;
  font-size:15px;padding:11px 30px;cursor:pointer;letter-spacing:.6px}
.btn:hover{background:#000}
.btn:disabled{background:var(--rule2);cursor:not-allowed}
.btn.ghost{background:#fff;color:var(--ink2);border:1px solid var(--rule2)}
.btn.ghost:hover{border-color:var(--ink3);color:var(--ink)}
.hint{font-size:11.8px;color:var(--ink3)}
.poolinfo{font-size:12.6px;color:var(--ink2);margin-top:12px}
.poolinfo b{color:var(--ink);font-family:var(--mono)}

/* ---------- 题目 ---------- */
.qhead{display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.qtag{font-family:var(--mono);font-size:11px;padding:2px 8px;border-radius:2px;
  background:var(--ink);color:var(--paper)}
.qtag.kp{background:rgba(0,0,0,.06);color:var(--ink2);cursor:pointer;border:1px solid var(--rule)}
.qtag.kp:hover{background:var(--ac,var(--acc));color:#fff}
.qtag.hot{background:#fff3e0;color:#96590a;border:1px solid #f0d3a8}
.stem{font-family:var(--serif);font-size:18.5px;line-height:1.85;letter-spacing:.2px;
  margin:0 0 20px;color:var(--ink)}
.qimg{margin:0 0 18px;text-align:center}
.qimg img{max-width:100%;height:auto;border:1px solid var(--rule);border-radius:4px;background:#fff}
.qimg .imtag{display:inline-block;margin-top:6px;font-family:var(--mono);font-size:10.5px;
  color:var(--ink3);letter-spacing:.5px}
.opts{display:flex;flex-direction:column;gap:9px}
.opt{display:grid;grid-template-columns:30px 1fr;gap:12px;align-items:start;
  border:1px solid var(--rule2);background:#fff;border-radius:4px;padding:12px 14px;
  cursor:pointer;text-align:left;font:inherit;font-size:14.8px;color:var(--ink);
  transition:.13s;position:relative}
.opt:hover:not(.done){border-color:var(--ink2);background:#fffdf8}
.opt .L{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--ink3);
  border-right:1px solid var(--rule);padding-right:8px}
.opt.sel{border-color:var(--sel);background:var(--selbg)}
.opt.sel .L{color:var(--sel)}
.opt.correct{border-color:var(--ok);background:var(--okbg)}
.opt.correct .L{color:var(--ok)}
.opt.wrong{border-color:var(--bad);background:var(--badbg)}
.opt.wrong .L{color:var(--bad)}
.opt.done{cursor:default}
.opt .mk{position:absolute;right:12px;top:50%;transform:translateY(-50%);font-size:15px;font-weight:700}
.opt.correct .mk{color:var(--ok)} .opt.wrong .mk{color:var(--bad)}

.reveal{margin-top:18px;border-top:1px dashed var(--rule2);padding-top:15px;
  animation:rise .22s ease-out}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.verdict{font-family:var(--serif);font-size:17px;font-weight:600;margin:0 0 8px}
.verdict.ok{color:var(--ok)} .verdict.bad{color:var(--bad)}
.ex{font-size:13.6px;color:var(--ink2);line-height:1.85;margin:0 0 4px}
.ex b{color:var(--ink)}
.nav{margin-top:18px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}

/* ---------- 结果 ---------- */
.big{font-family:var(--serif);font-size:54px;font-weight:600;letter-spacing:2px;margin:8px 0 0}
.bigsub{color:var(--ink3);font-size:12.5px;font-family:var(--mono);margin-bottom:22px}
table.res{width:100%;border-collapse:collapse;font-size:13.2px;margin:10px 0 20px}
table.res th,table.res td{border-bottom:1px solid var(--rule);padding:7px 6px;text-align:left}
table.res th{font-size:10.5px;letter-spacing:1.2px;color:var(--ink3);font-family:var(--mono);
  text-transform:uppercase;border-bottom:1px solid var(--rule2)}
table.res td.n{font-family:var(--mono);text-align:right;white-space:nowrap}
.badge{display:inline-block;font-family:var(--mono);font-size:11px;padding:1px 7px;border-radius:2px}
.badge.g{background:var(--okbg);color:var(--ok)} .badge.r{background:var(--badbg);color:var(--bad)}
.rev{border-bottom:1px solid var(--rule);padding:9px 0}
.rev .top{display:flex;gap:8px;align-items:center;font-size:12px;font-family:var(--mono);color:var(--ink3)}
.rev .st{font-size:13.4px;margin:3px 0;color:var(--ink)}
.rev .an{font-size:12.4px;color:var(--ink2)}
.rev .an b.ok{color:var(--ok)} .rev .an b.no{color:var(--bad)}
@media (max-width:640px){
  main{padding:18px 13px 100px}
  .stem{font-size:16.5px}
  .bar{padding:8px 12px;gap:7px}
  .bar .ttl{font-size:14px}
  .big{font-size:44px}
}
@media print{.bar,.pbar,.go,.nav{display:none}}

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
<div class="bar">
  <span class="ttl">408 刷题</span>
  <span class="prog" id="prog"></span>
  <span class="score" id="score"></span>
  <span class="right">
    <a href="index.html">入口</a>
    <a href="browse.html">题库</a>
    <button class="lnk" id="quit">退出</button>
  </span>
</div>
<div class="pbar"><i id="pfill"></i></div>
<main id="app"></main>

<script id="payload" type="application/json">__DATA__</script>
<script>
(function(){
  const P = JSON.parse(document.getElementById('payload').textContent);
  const Q = P.rows, META = P.meta, SUBJ = P.subj, TOPICS = P.topics, NY = P.y;
  const ACC = {DS:'#1f5fa8',CO:'#a83226',OS:'#1c6b3c',NET:'#96650a'};
  const LW='dsh408_wrong_v1', LS='dsh408_stat_v1';
  const $ = s=>document.querySelector(s);
  const app = $('#app');

  let wrong = loadJSON(LW, {});
  let stat  = loadJSON(LS, {n:0, ok:0});
  let S = {on:false};

  function loadJSON(k,d){ try{ return JSON.parse(localStorage.getItem(k)) ?? d; }catch(e){ return d; } }
  function saveJSON(k,v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

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
  const kOf = r=>r.y+'-'+r.q;
  function shuffle(a){ a=a.slice(); for(let i=a.length-1;i>0;i--){const j=Math.random()*(i+1)|0;[a[i],a[j]]=[a[j],a[i]];} return a; }

  /* ============ 题库索引 ============ */
  const bySubj={}, byChap={}, byKp={}, byYear={};
  Q.forEach(r=>{
    bySubj[r.s]=(bySubj[r.s]||0)+1;
    byChap[r.s+'|'+r.ch]=(byChap[r.s+'|'+r.ch]||0)+1;
    if(!byKp[r.kp]) byKp[r.kp]={n:0,name:r.kn,ch:r.ch,s:r.s};
    byKp[r.kp].n++;
    byYear[r.y]=(byYear[r.y]||0)+1;
  });
  const hotSet = k => (META[k]||{ny:0}).ny;

  /* ============ 起手页 ============ */
  function home(pre){
    S={on:false};
    pre = pre||{};
    const st={bank:'all', subj:null, chap:null, kp:null, year:null, topic:null,
              freq:null, order:'shuffle', grade:'instant', count:20};
    if(pre.kp){ st.bank='kp'; st.kp=pre.kp; }
    else if(pre.chap){ st.bank='chap'; st.chap=pre.chap; }
    else if(pre.subj){ st.bank='subj'; st.subj=pre.subj; }
    else if(pre.year){ st.bank='year'; st.year=+pre.year; }
    else if(pre.freq){ st.bank='freq'; st.freq=pre.freq; }
    else if(pre.topic){ st.bank='topic'; st.topic=pre.topic; }
    else if(pre.wrong){ st.bank='wrong'; }
    const modes=[['all','全部题目'],['topic','专题题库'],['subj','按科目'],
                 ['chap','按章节'],['kp','按知识点'],['year','按年份'],
                 ['freq','按考频'],['wrong','错题本']];
    app.innerHTML = `
      <h1>选一个题库，直接开刷</h1>
      <p class="lede">共 <b>${Q.length}</b> 道单选题（2009–2026，答案取自各年官方解析）。
        先选题库范围（可下钻到单个知识点），再选刷题格式。</p>

      <div class="step"><label><i>1</i>题库范围</label>
        <div class="seg" id="banks">
          ${modes.map(([m,t])=>`<button data-b="${m}" class="${st.bank===m?'on':''}">${t}</button>`).join('')}
        </div>
        <div id="panel"></div>
      </div>

      <div class="step"><label><i>2</i>刷题格式</label>
        <div class="seg" id="order">
          <button data-v="shuffle" class="on">乱序</button>
          <button data-v="year">按年份顺序</button>
        </div>
      </div>

      <div class="step"><label><i>3</i>判分方式</label>
        <div class="seg" id="grade">
          <button data-v="instant" class="on">即时判分（边做边看解析）</button>
          <button data-v="exam">交卷判分（整套做完再对答案）</button>
        </div>
      </div>

      <div class="step"><label><i>4</i>题量</label>
        <div class="seg" id="counts">
          <button data-c="10">10</button><button data-c="20" class="on">20</button>
          <button data-c="50">50</button><button data-c="0">全部</button>
        </div>
      </div>

      <div class="go">
        <button class="btn" id="start">开始刷题</button>
        <span class="hint">键盘 <b>1–4</b>/<b>A–D</b> 选择 · <b>Enter</b> 下一题</span>
      </div>
      <p class="poolinfo" id="pool"></p>`;

    const panel=$('#panel');
    function drawPanel(){
      if(st.bank==='all'||st.bank==='wrong'||st.bank==='freq'||st.bank==='topic'){
        if(st.bank==='topic'){
          panel.innerHTML=`<div class="panel"><div class="rows" id="rl">
            ${TOPICS.map(t=>`<button data-v="${t.id}" class="${st.topic===t.id?'on':''}">${esc(t.name)}<small>${t.n}</small></button>`).join('')}
            </div><p class="crumbline" id="tdesc">选一个专题：把相关知识点打包一起刷。</p></div>`;
          $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
            $('#rl').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
            st.topic=b.dataset.v;
            const t=TOPICS.find(x=>x.id===st.topic);
            $('#tdesc').innerHTML=`<b>${esc(t.name)}</b> · ${esc(t.desc)}`;
            pool();};
        } else if(st.bank==='freq'){
          panel.innerHTML=`<div class="panel"><div class="rows" id="rl">
            <button data-v="must" class="${st.freq==='must'?'on':''}">必考级（≥14/18 年）<small>${freqCount('must')}</small></button>
            <button data-v="high" class="${st.freq==='high'?'on':''}">高频（10–13 年）<small>${freqCount('high')}</small></button>
            <button data-v="common" class="${st.freq==='common'?'on':''}">常考（6–9 年）<small>${freqCount('common')}</small></button>
            <button data-v="rare" class="${st.freq==='rare'?'on':''}">低频（≤5 年）<small>${freqCount('rare')}</small></button>
          </div></div>`;
          $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
            $('#rl').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
            st.freq=b.dataset.v;pool();};
        } else if(st.bank==='wrong'){
          panel.innerHTML=`<div class="panel"><p class="crumbline">错题本现有 <b>${Object.keys(wrong).length}</b> 道。
            答对不会自动移除，方便反复练。</p></div>`;
        } else panel.innerHTML='';
        pool(); return;
      }
      if(st.bank==='subj'){
        panel.innerHTML=`<div class="panel"><div class="rows" id="rl">
          ${Object.keys(SUBJ).filter(k=>bySubj[k]).map(k=>
            `<button data-v="${k}" class="${st.subj===k?'on':''}" style="--ac:${ACC[k]}">${SUBJ[k]}<small>${bySubj[k]}</small></button>`).join('')}
          </div></div>`;
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          $('#rl').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
          st.subj=b.dataset.v;pool();};
      }
      if(st.bank==='chap'){
        const byS={};
        Object.keys(byChap).forEach(ck=>{const[s,c]=ck.split('|');(byS[s]=byS[s]||[]).push([c,ck]);});
        panel.innerHTML=`<div class="panel"><div class="rows" id="rl">
          ${Object.keys(byS).flatMap(s=>byS[s].sort((a,b)=>
            byChap[b[1]]-byChap[a[1]]).map(([c,ck])=>
            `<button data-v="${esc(ck)}" class="${st.chap===ck?'on':''}" style="--ac:${ACC[s]}">${esc(c)}<small>${byChap[ck]}</small></button>`)).join('')}
          </div></div>`;
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          $('#rl').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
          st.chap=b.dataset.v;pool();};
      }
      if(st.bank==='kp'){
        const list=Object.keys(byKp).sort((a,b)=>{
          const A=byKp[a],B=byKp[b];
          if(A.s!==B.s) return A.s.localeCompare(B.s);
          if(A.ch!==B.ch) return A.ch.localeCompare(B.ch);
          return B.n-A.n;
        });
        panel.innerHTML=`<div class="panel">
          <div class="rows" id="rl">
          ${list.map(k=>{const v=byKp[k];const hot=hotSet(k)>=14?'【必】':(hotSet(k)>=10?'【高】':'');
            return `<button data-v="${k}" class="${st.kp===k?'on':''}" style="--ac:${ACC[v.s]}">${hot}${esc(v.name)}<small>${v.n}</small></button>`;}).join('')}
          </div></div>`;
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          $('#rl').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
          st.kp=b.dataset.v;pool();};
      }
      if(st.bank==='year'){
        const ys=Object.keys(byYear).sort();
        panel.innerHTML=`<div class="panel"><div class="rows" id="rl">
          ${ys.map(y=>`<button data-v="${y}" class="${st.year==y?'on':''}">${y} 年<small>${byYear[y]}</small></button>`).join('')}
          </div></div>`;
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          $('#rl').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
          st.year=+b.dataset.v;pool();};
      }
      pool();
    }
    function freqCount(kind){
      return Q.filter(r=>{
        const ny=hotSet(r.kp);
        if(kind==='must') return ny>=14;
        if(kind==='high') return ny>=10&&ny<14;
        if(kind==='common') return ny>=6&&ny<10;
        return ny<6;
      }).length;
    }
    function pool0(){
      let p=Q.slice();
      if(st.bank==='topic'&&st.topic){
        const t=TOPICS.find(x=>x.id===st.topic);
        const set=new Set(t.kps); p=p.filter(r=>set.has(r.kp));
      }
      if(st.bank==='subj'&&st.subj) p=p.filter(r=>r.s===st.subj);
      if(st.bank==='chap'&&st.chap) p=p.filter(r=>r.s+'|'+r.ch===st.chap);
      if(st.bank==='kp'&&st.kp) p=p.filter(r=>r.kp===st.kp);
      if(st.bank==='year'&&st.year) p=p.filter(r=>r.y===st.year);
      if(st.bank==='wrong') p=p.filter(r=>wrong[kOf(r)]);
      if(st.bank==='freq'&&st.freq){
        p=p.filter(r=>{
          const ny=hotSet(r.kp);
          if(st.freq==='must') return ny>=14;
          if(st.freq==='high') return ny>=10&&ny<14;
          if(st.freq==='common') return ny>=6&&ny<10;
          return ny<6;
        });
      }
      return p;
    }
    function pool(){
      const n=pool0().length;
      const el=$('#pool'); if(!el) return;
      el.innerHTML=`当前题库 <b>${n}</b> 题` +
        (st.count>0 && n>st.count ? ` · 本次随机抽 <b>${st.count}</b> 道` : ' · 全部练习') +
        (st.grade==='exam' ? ` · 交卷判分` : ' · 即时判分');
    }

    $('#banks').onclick=e=>{const b=e.target.closest('button');if(!b)return;
      $('#banks').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
      st.bank=b.dataset.b;
      st.subj=st.chap=st.kp=st.year=null; st.topic=null; st.freq=null;
      drawPanel();};
    $('#order').onclick=e=>{const b=e.target.closest('button');if(!b)return;
      $('#order').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
      st.order=b.dataset.v;pool();};
    $('#grade').onclick=e=>{const b=e.target.closest('button');if(!b)return;
      $('#grade').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
      st.grade=b.dataset.v;pool();};
    $('#counts').onclick=e=>{const b=e.target.closest('button');if(!b)return;
      $('#counts').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
      st.count=+b.dataset.c;pool();};

    $('#start').onclick=()=>{
      let p=pool0();
      if(!p.length){ alert('这个题库暂时没有题目，换一个范围试试。'); return; }
      if(st.order==='shuffle') p=shuffle(p);
      else p=p.slice().sort((a,b)=> a.y-b.y || a.q-b.q);
      if(st.count>0 && p.length>st.count) p=p.slice(0,st.count);
      begin(p, st.grade);
    };
    drawPanel();
    $('#prog').textContent=''; $('#score').textContent=''; $('#pfill').style.width='0';
  }

  /* ============ 刷题 ============ */
  function begin(list, grade){
    S={on:true, list, grade, i:0, picks:new Array(list.length).fill(null),
       t0:Date.now()};
    render();
  }

  function render(){
    if(S.i>=S.list.length) return finish();
    const r=S.list[S.i], m=META[r.kp]||{ny:0}, pk=S.picks[S.i];
    const hot = m.ny>=14?'【必考】':(m.ny>=10?'【高频】':'');
    const graded = S.grade==='instant' && pk;
    app.innerHTML=`
      <div class="qhead">
        <span class="qtag">${r.y} 第 ${r.q} 题</span>
        <span class="qtag" style="background:${ACC[r.s]};color:#fff">${SUBJ[r.s]}</span>
        <span class="qtag kp" data-kp="${r.kp}" style="--ac:${ACC[r.s]}">${esc(r.kn)}</span>
        ${hot?`<span class="qtag hot">${hot} ${m.ny}/${NY} 年</span>`:''}
      </div>
      <div class="stem rt">${richText(r.st)}</div>
      ${r.im?`<div class="qimg"><img loading="lazy" src="${r.im}" alt="本题插图">`+
        (r.imscan?'<span class="imtag">原卷截图</span>':'')+'</div>':''}
      <div class="opts" id="opts">
        ${r.op.map((o,i)=>{const L='ABCD'[i];
          let cls='opt';
          if(graded){
            if(L===r.a) cls+=' correct done';
            else if(L===pk) cls+=' wrong done';
            else cls+=' done';
          } else if(pk===L) cls+=' sel';
          const mk = graded ? (L===r.a?'<span class="mk">✓</span>':(L===pk?'<span class="mk">✗</span>':'')) : '';
          return `<button class="${cls}" data-i="${i}"><span class="L">${L}</span>
                  <span class="T">${esc(o)}</span>${mk}</button>`;}).join('')}
      </div>
      <div id="rv"></div>`;
    $('#opts').onclick=e=>{const b=e.target.closest('.opt');
      if(!b||b.classList.contains('done'))return; choose('ABCD'[+b.dataset.i]);};
    const kpEl=app.querySelector('.qtag.kp');
    if(kpEl) kpEl.onclick=e=>{e.stopPropagation();
      location.href='browse.html#kp='+encodeURIComponent(r.kp);};

    if(graded) reveal(pk);
    else if(S.grade==='exam') navOnly();
    else navOnly(true);
    bar();
  }

  function choose(choice){
    const i=S.i, r=S.list[i];
    if(S.grade==='instant'){
      if(S.picks[i]) return;
      S.picks[i]=choice;
      const ok = choice===r.a;
      stat.n++; if(ok) stat.ok++;
      saveJSON(LS, stat);
      if(ok) delete wrong[kOf(r)]; else wrong[kOf(r)]=1;
      saveJSON(LW, wrong);
      render();
      return;
    }
    S.picks[i]=choice;
    render();
  }

  function reveal(choice){
    const r=S.list[S.i], ok=choice===r.a, m=META[r.kp]||{ny:0};
    const last=S.i+1>=S.list.length;
    $('#rv').innerHTML=`
      <div class="reveal">
        <p class="verdict ${ok?'ok':'bad'}">${ok?'回答正确':'回答错误'} · 正确答案 ${r.a}</p>
        ${r.ex?`<div class="ex rt"><b>解析：</b>${richText(r.ex)}</div>`:''}
        <p class="ex" style="color:#8a7f72">考点：${esc(r.kn)}（${esc(r.ch)}）· 该考点 ${NY} 年中出现 ${m.ny} 次</p>
      </div>`;
    navOnly(false, last);
  }

  function navOnly(maySkip, last){
    last = last!==undefined ? last : (S.i+1>=S.list.length);
    const el=$('#rv');
    const prev = S.i>0 ? '<button class="btn ghost" id="prev">上一题</button>' : '';
    const nextTxt = last ? (S.grade==='exam'?'交卷':'查看成绩') : '下一题';
    const disabled = (maySkip && S.i+1>=S.list.length) ? '' : '';
    const html = `<div class="nav">${prev}
        <button class="btn" id="next" ${disabled}>${nextTxt}</button>
        ${S.grade==='exam'?`<button class="btn ghost" id="submit">立即交卷</button>`:''}
        <span class="hint">${S.grade==='exam'?'可随时改答案':'Enter 下一题'}</span>
      </div>`;
    if(el) el.innerHTML = html; else app.insertAdjacentHTML('beforeend', html);
    const nx=$('#next'); if(nx) nx.onclick=()=>{S.i++;render();};
    const pv=$('#prev'); if(pv) pv.onclick=()=>{ if(S.i>0){S.i--;render();} };
    const sb=$('#submit'); if(sb) sb.onclick=()=>{ finish(); };
    if(nx) nx.focus();
  }

  function bar(){
    const n=S.list.length;
    const done=S.picks.filter(x=>x).length;
    $('#prog').textContent=`第 ${Math.min(S.i+1,n)} / ${n} 题`;
    $('#pfill').style.width=Math.round(done/n*100)+'%';
    const secs=Math.round((Date.now()-S.t0)/1000);
    const mm=String(Math.floor(secs/60)).padStart(2,'0'), ss=String(secs%60).padStart(2,'0');
    if(S.grade==='instant'){
      let ok=0; S.list.forEach((r,idx)=>{ if(S.picks[idx]===r.a) ok++; });
      const answered=S.picks.filter(x=>x).length;
      $('#score').innerHTML=`正确 <b>${ok}</b>/${answered} · ${mm}:${ss}`;
    } else {
      $('#score').innerHTML=`已答 <b>${done}</b>/${n} · ${mm}:${ss}`;
    }
  }

  /* ============ 结果 ============ */
  function finish(){
    const n=S.list.length;
    let ok=0;
    const recs=S.list.map((r,i)=>{
      const pick=S.picks[i];
      const good = pick===r.a;
      if(good) ok++;
      if(S.grade!=='instant'){
        if(good) delete wrong[kOf(r)]; else if(pick) wrong[kOf(r)]=1; else wrong[kOf(r)]=1;
      }
      return {r, pick, good};
    });
    if(S.grade!=='instant'){
      const answered=recs.filter(x=>x.pick).length;
      stat.n+=answered; stat.ok+=recs.filter(x=>x.good).length;
      saveJSON(LS,stat); saveJSON(LW,wrong);
    }
    S.on=false;
    const pct=Math.round(ok/Math.max(n,1)*100);
    const secs=Math.round((Date.now()-S.t0)/1000);
    const byCh={};
    recs.forEach(x=>{
      const k=x.r.s+'|'+x.r.ch; byCh[k]=byCh[k]||{n:0,ok:0};
      byCh[k].n++; if(x.good) byCh[k].ok++;
    });
    const rows=Object.entries(byCh).sort((a,b)=>a[1].ok/a[1].n-b[1].ok/b[1].n)
      .map(([k,v])=>{const[s,ch]=k.split('|');const p=Math.round(v.ok/v.n*100);
        return `<tr><td><span style="color:${ACC[s]}">■</span> ${esc(ch)}</td>
          <td class="n">${v.ok}/${v.n}</td>
          <td class="n"><span class="badge ${p>=80?'g':'r'}">${p}%</span></td></tr>`;}).join('');
    const bad=recs.filter(x=>!x.good);
    app.innerHTML=`
      <h1>本轮成绩</h1>
      <div class="big">${ok} / ${n}</div>
      <div class="bigsub">正确率 ${pct}% · 用时 ${Math.floor(secs/60)} 分 ${secs%60} 秒 ·
        累计 ${stat.ok}/${stat.n}（${Math.round(stat.ok/Math.max(stat.n,1)*100)}%）</div>
      ${rows?`<table class="res"><thead><tr><th>章节</th>
        <th style="text-align:right">正确</th><th style="text-align:right">正确率</th>
        </tr></thead><tbody>${rows}</tbody></table>`:''}
      ${bad.length?`<h3 style="font-family:var(--serif);font-size:17px;margin:22px 0 2px">
        错题回顾（${bad.length}）</h3>
        ${bad.map(x=>`<div class="rev">
          <div class="top"><span>${x.r.y}-${x.r.q}</span>
            <a href="browse.html#q=${x.r.y}-${x.r.q}" target="_blank"
               style="color:#1f5fa8;text-decoration:none">原题</a>
            <span>${esc(x.r.kn)}</span></div>
          <div class="st">${esc(x.r.st.slice(0,110))}${x.r.st.length>110?'…':''}</div>
          <div class="an">你选 <b class="no">${x.pick||'未答'}</b> · 正确 <b class="ok">${x.r.a}</b>
            ${x.r.ex?` · ${esc(x.r.ex.slice(0,150))}${x.r.ex.length>150?'…':''}`:''}</div>
        </div>`).join('')}`:`<p class="ex" style="margin-top:18px">本轮全部正确。</p>`}
      <div class="go">
        <button class="btn" id="again">再用同一题库刷一轮</button>
        <button class="btn ghost" id="onlywrong">只练错题（${Object.keys(wrong).length}）</button>
        <button class="btn ghost" id="home">换一个题库</button>
      </div>`;
    const list=S.list;
    $('#again').onclick=()=>begin(S.grade==='instant'?shuffle(list):list, S.grade);
    $('#onlywrong').onclick=()=>{
      const p=Q.filter(r=>wrong[kOf(r)]);
      if(!p.length){ alert('错题本是空的。'); return; }
      begin(shuffle(p),'instant');
    };
    $('#home').onclick=home;
    $('#prog').textContent='完成'; $('#pfill').style.width='100%';
    $('#score').innerHTML=`正确 <b>${ok}</b>/${n}`;
  }

  /* ============ 键盘 ============ */
  document.addEventListener('keydown', e=>{
    if(!S.on) return;
    const nx=$('#next');
    if(e.key==='Enter' && nx){ e.preventDefault(); nx.click(); return; }
    const cur=S.picks[S.i];
    if(S.grade==='instant' && cur) return;
    const map={'1':'A','2':'B','3':'C','4':'D','a':'A','b':'B','c':'C','d':'D'};
    const v=map[(e.key||'').toLowerCase()];
    if(v){ e.preventDefault(); choose(v); }
  });
  $('#quit').onclick=()=>{
    if(S.on && S.picks && S.picks.some(x=>x) && !confirm('退出本轮？答题记录不会保存。')) return;
    home();
  };

  // 知识体系/题库页通过 ?kp= / ?chap= / ?subj= / ?year= / ?freq= / ?topic= 直达
  const qp=new URLSearchParams(location.search);
  home({kp:qp.get('kp')||null, chap:qp.get('chap')||null, subj:qp.get('subj')||null,
        year:qp.get('year')||null, freq:qp.get('freq')||null,
        topic:qp.get('topic')||null, wrong:qp.get('wrong')||null});
})();
</script>
</body>
</html>
"""


def main():
    rows = json.load(open(os.path.join(OUT, "data", "quiz.json"), encoding="utf-8"))
    summary = json.load(open(os.path.join(OUT, "data", "summary.json"), encoding="utf-8"))
    meta = {k["id"]: {"ny": k["n_years"], "p": k["points"], "c": k["count"]}
            for k in summary["kps"]}
    have = {}
    for r in rows:
        have[r["kp"]] = have.get(r["kp"], 0) + 1
    topics = []
    for tid, name, desc, kps in TOPICS:
        # 只保留本资料里确实有题的知识点，保证"N 个知识点"与题数自洽
        kps_have = [k for k in kps if have.get(k, 0)]
        n = sum(have.get(k, 0) for k in kps_have)
        if n:
            topics.append({"id": tid, "name": name, "desc": desc,
                           "kps": kps_have, "n": n})
    topics.sort(key=lambda t: -t["n"])

    payload = json.dumps(
        {"rows": rows, "meta": meta, "subj": SUBJECTS,
         "topics": topics, "y": len(summary["years"])},
        ensure_ascii=False, separators=(",", ":"),
    )
    payload = (payload.replace("<", "\\u003c")
                      .replace(">", "\\u003e")
                      .replace("&", "\\u0026"))
    html = TEMPLATE.replace("__DATA__", payload)
    dest = os.path.join(OUT, "quiz.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {dest}  {len(html.encode('utf-8'))/1024:.0f} KB  questions={len(rows)}")
    print("专题库：")
    for t in topics:
        print(f"  {t['name']:<18} {t['n']:>3} 题  ({len(t['kps'])} 个知识点)")


if __name__ == "__main__":
    main()

