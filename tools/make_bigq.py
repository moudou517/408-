# -*- coding: utf-8 -*-
"""Build out/bigq.html — 综合题(41-47) 练习：先看题干，按键再看参考答案与思路。

综合题没有单选答案，所以采用「自评」：显示答案后自己判断 会 / 不会，记录进大题错题本。
支持 ?kp= / ?chap= / ?subj= / ?year= 直达（知识体系页就是靠这个连过来的）。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syllabus import SUBJECTS  # noqa: E402

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")

TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>408 大题 · 综合题训练</title>
<style>
:root{
  --paper:#f6f2e9;--panel:#fcfaf5;--ink:#1a1613;--ink2:#4a423a;--ink3:#8a7f72;
  --rule:#e0d8c9;--rule2:#cfc4b0;--acc:#a83226;
  --ok:#1c6b3c;--okbg:#e6f4ea;--bad:#a83226;--badbg:#fbeeec;
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
  border-bottom:1px solid var(--rule);padding:10px 20px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.bar .ttl{font-family:var(--serif);font-size:16px;font-weight:600;letter-spacing:.4px}
.bar .prog{font-family:var(--mono);font-size:11.5px;color:var(--ink3)}
.bar .right{margin-left:auto;display:flex;gap:8px}
.bar a,.bar button.lnk{border:1px solid var(--rule2);background:#fff;border-radius:3px;
  font:inherit;font-size:12px;padding:4px 9px;color:var(--ink2);cursor:pointer;text-decoration:none}
.bar a:hover,.bar button.lnk:hover{border-color:var(--ink3);color:var(--ink)}
main{max-width:900px;margin:0 auto;padding:30px 20px 120px}

h1{font-family:var(--serif);font-size:28px;font-weight:600;letter-spacing:.8px;margin:2px 0 4px}
.lede{color:var(--ink2);font-size:13.4px;margin:0 0 20px}
.step{margin:0 0 16px}
.step>label{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:10.5px;
  letter-spacing:1.8px;color:var(--ink3);text-transform:uppercase;margin-bottom:7px}
.step>label i{width:15px;height:15px;border:1px solid var(--rule2);border-radius:50%;
  display:grid;place-items:center;font-style:normal;font-size:9px;color:var(--ink3)}
.seg{display:flex;flex-wrap:wrap;gap:5px}
.seg button{border:1px solid var(--rule2);background:#fff;border-radius:3px;font:inherit;
  font-size:13px;padding:6px 12px;cursor:pointer;color:var(--ink2);transition:.13s}
.seg button:hover{border-color:var(--ink3);color:var(--ink)}
.seg button.on{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.panel{margin:10px 0 0;padding:12px;background:#fff;border:1px solid var(--rule);border-radius:5px}
.rows{display:flex;flex-wrap:wrap;gap:6px;max-height:250px;overflow:auto}
.rows button{border:1px solid var(--rule);background:#fff;border-radius:2px;font:inherit;
  font-size:12.5px;padding:4px 9px;cursor:pointer;color:var(--ink2);text-align:left}
.rows button small{font-family:var(--mono);font-size:10px;color:var(--ink3);margin-left:5px}
.rows button:hover{border-color:var(--ink3);color:var(--ink)}
.rows button.on{background:#fbeeec;border-color:var(--acc);color:var(--ink);font-weight:600}
.go{margin-top:20px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;
  padding-top:16px;border-top:1px solid var(--rule)}
.btn{background:var(--ink);color:var(--paper);border:0;border-radius:3px;font:inherit;
  font-size:15px;padding:11px 28px;cursor:pointer;letter-spacing:.6px}
.btn:hover{background:#000}
.btn.ghost{background:#fff;color:var(--ink2);border:1px solid var(--rule2)}
.btn.ghost:hover{border-color:var(--ink3);color:var(--ink)}
.btn.reveal{background:var(--acc)}
.btn.reveal:hover{background:#8c2118}
.hint{font-size:11.8px;color:var(--ink3)}
.poolinfo{font-size:12.6px;color:var(--ink2);margin-top:10px}
.poolinfo b{color:var(--ink);font-family:var(--mono)}

/* 题目卡 */
.qhead{display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap}
.qtag{font-family:var(--mono);font-size:11px;padding:2px 8px;border-radius:2px;
  background:var(--ink);color:var(--paper)}
.qtag.kp{background:rgba(0,0,0,.06);color:var(--ink2);border:1px solid var(--rule)}
.qtag.pt{background:var(--acc);color:#fff}
.stem{font-family:var(--serif);font-size:16.6px;line-height:1.9;letter-spacing:.15px;
  margin:0 0 18px;color:var(--ink);white-space:pre-wrap;max-height:44vh;overflow:auto;
  padding-right:6px}
.qimg{margin:0 0 16px;text-align:center}
.qimg img{max-width:100%;height:auto;border:1px solid var(--rule);border-radius:4px;background:#fff}
.qimg .imtag{display:inline-block;margin-top:6px;font-family:var(--mono);font-size:10.5px;
  color:var(--ink3);letter-spacing:.5px}
.sol{margin-top:18px;border-top:2px solid var(--acc);padding-top:14px;animation:rise .22s ease-out}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.sol h4{margin:0 0 8px;font-family:var(--serif);font-size:16px;color:var(--acc);font-weight:600}
.solbody{font-size:14.2px;line-height:1.95;color:var(--ink2);white-space:pre-wrap;
  max-height:52vh;overflow:auto;padding-right:6px}
.sol .none{color:var(--ink3);font-size:13px}
.self{margin-top:18px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;
  padding-top:14px;border-top:1px dashed var(--rule2)}
.self .q{font-size:13.4px;color:var(--ink2);margin-right:4px}
.btn.yes{background:var(--ok)} .btn.yes:hover{background:#155a30}
.nav{margin-top:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.big{font-family:var(--serif);font-size:52px;font-weight:600;letter-spacing:2px;margin:8px 0 0}
.bigsub{color:var(--ink3);font-size:12.5px;font-family:var(--mono);margin-bottom:20px}
table.res{width:100%;border-collapse:collapse;font-size:13.2px;margin:10px 0 18px}
table.res th,table.res td{border-bottom:1px solid var(--rule);padding:7px 6px;text-align:left}
table.res th{font-size:10.5px;letter-spacing:1.2px;color:var(--ink3);font-family:var(--mono);
  text-transform:uppercase;border-bottom:1px solid var(--rule2)}
table.res td.n{font-family:var(--mono);text-align:right}
.rev{border-bottom:1px solid var(--rule);padding:9px 0}
.rev .top{display:flex;gap:8px;align-items:center;font-size:12px;font-family:var(--mono);color:var(--ink3)}
@media (max-width:640px){
  main{padding:16px 13px 100px}
  .stem{font-size:15.6px;max-height:36vh}
  .solbody{max-height:44vh}
  .big{font-size:42px}
}
@media print{.bar,.go,.nav,.self,.step{display:none}.stem,.solbody{max-height:none}}

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
  <span class="ttl">408 大题</span>
  <span class="prog" id="prog"></span>
  <span class="right">
    <a href="map.html">知识体系</a>
    <a href="quiz.html">刷选择</a>
    <a href="index.html">入口</a>
    <button class="lnk" id="quit">退出</button>
  </span>
</div>
<main id="app"></main>
<script id="payload" type="application/json">__DATA__</script>
<script>
(function(){
  const P = JSON.parse(document.getElementById('payload').textContent);
  const Q = P.rows, SUBJ = P.subj;
  const ACC = {DS:'#1f5fa8',CO:'#a83226',OS:'#1c6b3c',NET:'#96650a'};
  const LK='dsh408_bigq_v1';
  const $=s=>document.querySelector(s);
  const app=$('#app');
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

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
  const kOf=r=>r.y+'-'+r.q;
  let marks=load(LK,{});          // key -> 1(会) / 0(不会)
  let S={on:false};

  function load(k,d){try{return JSON.parse(localStorage.getItem(k))??d}catch(e){return d}}
  function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
  function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.random()*(i+1)|0;[a[i],a[j]]=[a[j],a[i]];}return a;}

  const bySubj={},byChap={},byKp={},byYear={};
  Q.forEach(r=>{
    bySubj[r.s]=(bySubj[r.s]||0)+1;
    byChap[r.s+'|'+r.ch]=(byChap[r.s+'|'+r.ch]||0)+1;
    if(!byKp[r.kp]) byKp[r.kp]={n:0,name:r.kn,s:r.s,ch:r.ch};
    byKp[r.kp].n++; byYear[r.y]=(byYear[r.y]||0)+1;
  });

  /* ---------- 起手页 ---------- */
  function home(pre){
    S={on:false};
    pre = pre||{};
    const st={bank:pre.kp?'kp':(pre.chap?'chap':(pre.subj?'subj':(pre.year?'year':'all'))),
              kp:pre.kp||null, chap:pre.chap||null, subj:pre.subj||null,
              year:pre.year||null, wrong:false, order:'shuffle'};
    const modes=[['all','全部综合题'],['subj','按科目'],['chap','按章节'],
                 ['kp','按知识点'],['year','按年份'],['wrong','大题错题本']];
    app.innerHTML=`
      <h1>综合题训练（41–47）</h1>
      <p class="lede">共 <b>${Q.length}</b> 道大题，<b>${Q.filter(r=>r.sol).length}</b> 道带参考答案与解析。
        先自己写思路，再按「显示参考答案与思路」对照，然后自评会不会。</p>

      <div class="step"><label><i>1</i>范围</label>
        <div class="seg" id="banks">
          ${modes.map(([m,t])=>`<button data-b="${m}" class="${st.bank===m?'on':''}">${t}</button>`).join('')}
        </div>
        <div id="panel"></div>
      </div>
      <div class="step"><label><i>2</i>顺序</label>
        <div class="seg" id="order">
          <button data-v="shuffle" class="on">乱序</button>
          <button data-v="year">按年份</button>
        </div>
      </div>
      <div class="go">
        <button class="btn" id="start">开始</button>
        <span class="hint">键盘 <b>空格/Enter</b> 显示答案 · <b>1</b> 会了 · <b>2</b> 不会</span>
      </div>
      <p class="poolinfo" id="pool"></p>`;

    function drawPanel(){
      const p=$('#panel');
      if(st.bank==='all'||st.bank==='wrong'){p.innerHTML='';pool();return;}
      const mk=(items,attr)=>`<div class="panel"><div class="rows" id="rl">${items}</div></div>`;
      if(st.bank==='subj'){
        p.innerHTML=mk(Object.keys(SUBJ).filter(k=>bySubj[k]).map(k=>
          `<button data-v="${k}" class="${st.subj===k?'on':''}" style="--ac:${ACC[k]}">
           ${SUBJ[k]}<small>${bySubj[k]}</small></button>`).join(''));
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          st.subj=b.dataset.v;drawPanel();};
      } else if(st.bank==='chap'){
        const byS={};Object.keys(byChap).forEach(ck=>{const[s,c]=ck.split('|');(byS[s]=byS[s]||[]).push([c,ck]);});
        p.innerHTML=mk(Object.keys(byS).flatMap(s=>byS[s].sort((a,b)=>byChap[b[1]]-byChap[a[1]])
          .map(([c,ck])=>`<button data-v="${esc(ck)}" class="${st.chap===ck?'on':''}"
            style="--ac:${ACC[s]}">${esc(c)}<small>${byChap[ck]}</small></button>`)).join(''));
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          st.chap=b.dataset.v;drawPanel();};
      } else if(st.bank==='kp'){
        const list=Object.keys(byKp).sort((a,b)=> a===st.kp?-1:(b===st.kp?1:byKp[b].n-byKp[a].n));
        p.innerHTML=mk(list.map(k=>{const v=byKp[k];return `<button data-v="${k}"
          class="${st.kp===k?'on':''}" style="--ac:${ACC[v.s]}">${esc(v.name)}<small>${v.n}</small></button>`}).join(''));
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          st.kp=b.dataset.v;drawPanel();};
      } else if(st.bank==='year'){
        p.innerHTML=mk(Object.keys(byYear).sort().map(y=>
          `<button data-v="${y}" class="${st.year==y?'on':''}">${y}<small>${byYear[y]}</small></button>`).join(''));
        $('#rl').onclick=e=>{const b=e.target.closest('button');if(!b)return;
          st.year=+b.dataset.v;drawPanel();};
      }
      pool();
    }
    function pool0(){
      let p=Q.slice();
      if(st.bank==='subj'&&st.subj)p=p.filter(r=>r.s===st.subj);
      if(st.bank==='chap'&&st.chap)p=p.filter(r=>r.s+'|'+r.ch===st.chap);
      if(st.bank==='kp'&&st.kp)p=p.filter(r=>r.kp===st.kp);
      if(st.bank==='year'&&st.year)p=p.filter(r=>r.y===st.year);
      if(st.bank==='wrong')p=p.filter(r=>marks[kOf(r)]===0);
      return p;
    }
    function pool(){const n=pool0().length;$('#pool').innerHTML=`当前 <b>${n}</b> 道大题`;}

    $('#banks').onclick=e=>{const b=e.target.closest('button');if(!b)return;
      $('#banks').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
      st.bank=b.dataset.b;st.subj=st.chap=st.kp=st.year=null;drawPanel();};
    $('#order').onclick=e=>{const b=e.target.closest('button');if(!b)return;
      $('#order').querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
      st.order=b.dataset.v;};
    $('#start').onclick=()=>{
      let p=pool0();
      if(!p.length){alert('这个范围没有大题，换一个试试。');return;}
      if(st.order==='shuffle')p=shuffle(p); else p=p.slice().sort((a,b)=>a.y-b.y||a.q-b.q);
      begin(p);
    };
    drawPanel();
    $('#prog').textContent='';
  }

  /* ---------- 刷题 ---------- */
  function begin(list){ S={on:true,list,i:0,revealed:false,judged:0,ok:0,t0:Date.now()}; render(); }

  function render(){
    if(S.i>=S.list.length) return finish();
    const r=S.list[S.i];
    app.innerHTML=`
      <div class="qhead">
        <span class="qtag">${r.y} 第 ${r.q} 题</span>
        <span class="qtag pt">${r.p} 分</span>
        <span class="qtag" style="background:${ACC[r.s]};color:#fff">${SUBJ[r.s]}</span>
        <span class="qtag kp">${esc(r.kn)}</span>
        ${marks[kOf(r)]===1?'<span class="qtag" style="background:#e6f4ea;color:#1c6b3c;border:1px solid #b7dfc4">标记过：会</span>':''}
      </div>
      <div class="stem rt">${richText(r.st)}</div>
      ${r.im?`<div class="qimg"><img loading="lazy" src="${r.im}" alt="本题插图">`+
        (r.imscan?'<span class="imtag">原卷截图</span>':'')+'</div>':''}
      <div id="solbox"></div>`;
    const bx=$('#solbox');
    if(S.revealed) showSol(r);
    else bx.innerHTML=`<div class="go" style="border-top:0;padding-top:0">
        <button class="btn reveal" id="rv">显示参考答案与思路</button>
        <span class="hint">先自己在纸上写完整思路，再对照</span></div>`;
    const rb=$('#rv'); if(rb) rb.onclick=()=>{S.revealed=true;render();};
    prog();
  }

  function showSol(r){
    const bx=$('#solbox');
    const mine=marks[kOf(r)];
    bx.innerHTML=`
      <div class="sol">
        <h4>参考答案与思路</h4>
        ${r.sol?`<div class="solbody rt">${richText(r.sol)}</div>`
               :`<div class="none">这一年的解析 PDF 是扫描件，暂未提取到文字版。
                  可在 <a href="browse.html#q=${r.y}-${r.q}" target="_blank">题库</a>
                  里对照原题手写，或直接翻解析 PDF。</div>`}
      </div>
      <div class="self">
        <span class="q">自评：这题我会了吗？</span>
        <button class="btn yes" id="yes">会了</button>
        <button class="btn ghost" id="no">不会，进错题本</button>
        <span class="hint">${mine===undefined?'':(mine===1?'上次：会':'上次：不会')}</span>
      </div>
      <div class="nav">
        ${S.i>0?'<button class="btn ghost" id="prev">上一题</button>':''}
        <button class="btn" id="next">${S.i+1>=S.list.length?'查看小结':'下一题'}</button>
      </div>`;
    $('#yes').onclick=()=>{mark(r,1);};
    $('#no').onclick=()=>{mark(r,0);};
    const pv=$('#prev'); if(pv) pv.onclick=()=>{if(S.i>0){S.i--;S.revealed=false;render();}};
    $('#next').onclick=()=>{S.i++;S.revealed=false;render();};
    const nx=$('#next'); if(nx) nx.focus();
  }

  function mark(r,val){
    marks[kOf(r)]=val; save(LK,marks);
    S.judged++; if(val===1) S.ok++;
    S.i++; S.revealed=false; render();
  }

  function prog(){
    $('#prog').textContent=`第 ${Math.min(S.i+1,S.list.length)} / ${S.list.length} 题`;
  }

  /* ---------- 小结 ---------- */
  function finish(){
    S.on=false;
    const n=S.list.length;
    const recs=S.list.map(r=>({r, m:marks[kOf(r)]}));
    const ok=recs.filter(x=>x.m===1).length;
    const judged=recs.filter(x=>x.m!==undefined).length;
    const bad=recs.filter(x=>x.m===0);
    const secs=Math.round((Date.now()-S.t0)/1000);
    app.innerHTML=`
      <h1>本轮小结</h1>
      <div class="big">${ok} / ${judged||0}</div>
      <div class="bigsub">自评「会」${ok} 道 · 已判定 ${judged} 道 · 共 ${n} 道 · 用时 ${Math.floor(secs/60)} 分 ${secs%60} 秒</div>
      ${bad.length?`<h3 style="font-family:var(--serif);font-size:17px;margin:18px 0 2px">需要再看一遍（${bad.length}）</h3>
        ${bad.map(x=>`<div class="rev"><div class="top"><span>${x.r.y}-${x.r.q}</span>
          <span>${esc(x.r.kn)}</span>
          <a href="browse.html#q=${x.r.y}-${x.r.q}" target="_blank" style="color:#a83226;text-decoration:none">原题</a>
          </div></div>`).join('')}`:''}
      <div class="go">
        <button class="btn" id="again">再来一轮</button>
        <button class="btn ghost" id="onlyno">只练不会的（${Object.values(marks).filter(v=>v===0).length}）</button>
        <button class="btn ghost" id="home">换一个范围</button>
      </div>`;
    $('#again').onclick=()=>begin(shuffle(S.list));
    $('#onlyno').onclick=()=>{
      const p=Q.filter(r=>marks[kOf(r)]===0);
      if(!p.length){alert('还没有标记"不会"的大题。');return;}
      begin(shuffle(p));
    };
    $('#home').onclick=()=>home({});
    $('#prog').textContent='小结';
  }

  /* ---------- 键盘 ---------- */
  document.addEventListener('keydown',e=>{
    if(!S.on) return;
    if(!S.revealed && (e.key===' '||e.key==='Enter')){ e.preventDefault();
      const b=$('#rv'); if(b) b.click(); return; }
    if(S.revealed){
      if(e.key==='1'){e.preventDefault();const b=$('#yes');if(b)b.click();}
      if(e.key==='2'){e.preventDefault();const b=$('#no');if(b)b.click();}
      if(e.key==='Enter'){e.preventDefault();const b=$('#next');if(b)b.click();}
    }
  });
  $('#quit').onclick=()=>{
    if(S.on && S.judged && !confirm('退出本轮？已自评的记录已保存。')) return;
    home({});
  };

  /* ---------- 启动（支持 ?kp= / ?chap= / ?subj= / ?year=） ---------- */
  const qp=new URLSearchParams(location.search);
  home({kp:qp.get('kp')||null, chap:qp.get('chap')||null,
        subj:qp.get('subj')||null, year:qp.get('year')?+qp.get('year'):null});
})();
</script>
</body>
</html>
"""


def main():
    p = os.path.join(OUT, "data", "bigq.json")
    rows = json.load(open(p, encoding="utf-8"))
    payload = json.dumps({"rows": rows, "subj": SUBJECTS},
                         ensure_ascii=False, separators=(",", ":"))
    payload = (payload.replace("<", "\\u003c")
                      .replace(">", "\\u003e")
                      .replace("&", "\\u0026"))
    html = TEMPLATE.replace("__DATA__", payload)
    dest = os.path.join(OUT, "bigq.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    with_sol = sum(1 for r in rows if r["sol"])
    print(f"wrote {dest}  {len(html.encode('utf-8'))/1024:.0f} KB  "
          f"bigq={len(rows)}  with解析={with_sol}")


if __name__ == "__main__":
    main()
