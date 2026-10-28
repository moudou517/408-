# -*- coding: utf-8 -*-
"""Build out/index.html — the single entry point.

三个门：知识体系 / 题库 / 刷题；右上角「平板连接」弹出二维码。
"""

import json
import os

ROOT = r"E:\CST\408"
OUT = os.path.join(ROOT, "out")

CSS = """
:root{--paper:#f6f2e9;--panel:#fcfaf5;--ink:#1a1613;--ink2:#4a423a;--ink3:#8a7f72;
 --rule:#e0d8c9;--rule2:#cfc4b0;--acc:#1f5fa8;--big:#a83226;
 --serif:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",Georgia,serif;
 --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Segoe UI",sans-serif;
 --mono:"Cascadia Mono",Consolas,"Courier New",monospace;}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:var(--paper);color:var(--ink);
 font-family:var(--sans);font-size:15px;line-height:1.75;display:flex;
 justify-content:center;padding:26px 18px 40px;
 background-image:radial-gradient(rgba(160,140,110,.06) 1px,transparent 1px);background-size:3px 3px;}
.shell{width:100%;max-width:820px}
.kicker{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:10.5px;
 letter-spacing:2px;color:var(--ink3);text-transform:uppercase;margin-bottom:10px}
.kicker .sp{flex:1}
.qrbtn{border:1px solid var(--rule2);background:#fff;border-radius:999px;font:inherit;
 font-size:11.5px;padding:4px 12px;color:var(--ink2);cursor:pointer;letter-spacing:0;
 text-transform:none;font-family:var(--sans)}
.qrbtn:hover{border-color:var(--ink3);color:var(--ink)}
h1{font-family:var(--serif);font-size:31px;font-weight:600;margin:0 0 6px;letter-spacing:.8px}
.lede{color:var(--ink2);font-size:13.4px;margin:0 0 4px}
.stat{font-family:var(--mono);font-size:11.5px;color:var(--ink3);margin:10px 0 22px;
 padding-bottom:16px;border-bottom:1px solid var(--rule)}
.stat b{color:var(--ink);font-size:13px}

.doors{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.door{display:block;text-decoration:none;color:inherit;border:1px solid var(--rule);
 background:var(--panel);padding:16px 18px;position:relative;transition:.16s;overflow:hidden}
.door:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--ac);
 transform:scaleY(0);transform-origin:top;transition:transform .18s}
.door:hover{border-color:var(--rule2);background:#fff;box-shadow:0 10px 26px -18px rgba(60,45,25,.6)}
.door:hover:before{transform:scaleY(1)}
.door .no{font-family:var(--mono);font-size:10.5px;color:var(--ink3);letter-spacing:1.5px}
.door .t{font-family:var(--serif);font-size:19px;font-weight:600;letter-spacing:.5px;margin:2px 0 3px}
.door .d{font-size:12.3px;color:var(--ink3);line-height:1.6}
.door .n{font-family:var(--mono);font-size:11px;color:var(--ink2);margin-top:8px}
.door .n b{color:var(--ac);font-size:13px}
.door.wide{grid-column:1 / -1}
.pair{display:flex;gap:10px;margin-top:10px}
.pair a{flex:1;display:block;text-decoration:none;text-align:center;border:1px solid var(--rule2);
 background:#fff;padding:9px 6px;font-size:13px;color:var(--ink2);transition:.14s}
.pair a:hover{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.pair a b{font-family:var(--mono);font-size:14px;display:block}

.sub{margin:22px 0 0;padding-top:16px;border-top:1px solid var(--rule)}
.sub .h{font-family:var(--mono);font-size:10.5px;letter-spacing:1.6px;color:var(--ink3);
 text-transform:uppercase;margin-bottom:8px}
.sub .links{display:flex;flex-wrap:wrap;gap:8px}
.sub a{font-size:12.5px;color:var(--ink2);text-decoration:none;border:1px solid var(--rule2);
 background:#fff;border-radius:999px;padding:4px 12px}
.sub a:hover{border-color:var(--acc);color:var(--acc)}
.foot{margin-top:22px;font-size:11px;color:var(--ink3);font-family:var(--mono);line-height:1.95}

/* 二维码弹窗 */
.mask{position:fixed;inset:0;background:rgba(26,22,19,.5);display:none;z-index:100;
 align-items:center;justify-content:center;padding:18px;backdrop-filter:blur(3px)}
.mask.on{display:flex}
.modal{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:22px 26px;
 max-width:360px;width:100%;text-align:center;box-shadow:0 30px 70px -30px rgba(0,0,0,.5)}
.modal h3{font-family:var(--serif);font-size:18px;margin:0 0 4px;font-weight:600}
.modal p{font-size:12px;color:var(--ink3);margin:0 0 14px}
.modal img{width:210px;height:210px;border:1px solid var(--rule);background:#fff;display:block;margin:0 auto 12px}
.modal .url{font-family:var(--mono);font-size:13.5px;background:#fff;border:1px solid var(--rule2);
 border-radius:4px;padding:8px 10px;user-select:all;word-break:break-all;display:block;margin-bottom:8px}
.modal .row{display:flex;gap:8px}
.modal .row button{flex:1;border:1px solid var(--rule2);background:#fff;border-radius:3px;
 font:inherit;font-size:12.5px;padding:7px;cursor:pointer;color:var(--ink2)}
.modal .row button:hover{border-color:var(--ink3);color:var(--ink)}
.modal .row button.pri{background:var(--ink);border-color:var(--ink);color:var(--paper)}
@media (max-width:640px){
  body{padding:18px 13px 30px}
  h1{font-size:25px}
  .doors{grid-template-columns:1fr}
  .door.wide{grid-column:auto}
}
@media print{body{background:#fff}.qrbtn{display:none}}
"""

TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>408 真题复习中心</title>
<style>__CSS__</style></head><body>
<div class="shell">
  <div class="kicker"><span>408 / 真题复习中心</span><span class="sp"></span>
    <button class="qrbtn" id="qrOpen">📱 平板连接</button></div>
  <h1>408 真题复习中心</h1>
  <p class="lede">先看知识体系，再按考点刷题；也可以直接检索整套题库。</p>
  <div class="stat"><b>__NQ__</b> 道真题 · <b>__NBIG__</b> 道综合题 · <b>__NKP__</b> 个考纲知识点 ·
    <b>__NY__</b> 套卷（2009–2026）</div>

  <div class="doors">
    <a class="door" href="map.html" style="--ac:#1f5fa8">
      <div class="no">01 / FRAMEWORK</div>
      <div class="t">知识体系</div>
      <div class="d">四科 → 章 → 知识点。每个知识点都能一键跳进对应题库。</div>
      <div class="n"><b>116</b> 个知识点 · 含【必考】/【高频】标记</div>
    </a>
    <a class="door" href="browse.html" style="--ac:#96650a">
      <div class="no">02 / BANK</div>
      <div class="t">题库</div>
      <div class="d">按科目/章/知识点检索全部真题，综合题也带参考答案与解析。</div>
      <div class="n"><b>__NQ__</b> 道题 · 可搜索、可直达</div>
    </a>
    <div class="door wide" style="--ac:#1c6b3c">
      <div class="no">03 / PRACTICE</div>
      <div class="t">刷题</div>
      <div class="d">两种模式：选择题即时判分，综合题先写思路再看参考答案。</div>
      <div class="pair">
        <a href="quiz.html"><b>__NSEL__</b>选择题 · 即时判分</a>
        <a href="bigq.html"><b>__NBIG__</b>综合题 · 显示答案</a>
      </div>
    </div>
  </div>

  <div class="sub">
    <div class="h">Reference</div>
    <div class="links">
      <a href="report.html">完整分析报告</a>
      <a href="408_题库索引.pdf">题库索引 PDF</a>
      <a href="408_图表集.pdf">图表集 PDF</a>
      <a href="connect.html">平板连接说明</a>
      <a href="README.md">交付说明</a>
    </div>
  </div>

  <div class="foot">
    答案与解析取自你提供的各年《真题解析》· 练习记录存在浏览器本地，按设备各存一份<br>
    原件：E:\\CST\\408\\out\\
  </div>
</div>

<div class="mask" id="qrMask">
  <div class="modal">
    <h3>平板连接</h3>
    <p id="qrTip">平板与电脑连同一 Wi-Fi，相机对着二维码扫一下；或手输下面的地址。</p>
    <img id="qrImg" src="qr_quiz.png" alt="二维码" onerror="qrOff()">
    <span class="url" id="qrUrl">__URL__</span>
    <div class="row">
      <button id="qrCopy">复制地址</button>
      <button class="pri" id="qrClose">关闭</button>
    </div>
  </div>
</div>

<script>
/* 静态副本（GitHub Pages / 直接拷走）没有 qr_quiz.png 与 connect.json，
   降级成文字说明，避免出现坏图和写死的旧 IP */
window.qrOff=function(){
  var i=document.getElementById('qrImg'); if(i){ i.style.display='none'; }
  var t=document.getElementById('qrTip');
  if(t){ t.textContent='当前是静态副本，没有二维码；平板连接需要在本机运行 tools/serve.py。'; }
  var u=document.getElementById('qrUrl');
  if(u){ u.textContent='本机运行：python tools/serve.py 8000'; }
};
(function(){
  var open=document.getElementById('qrOpen'), mask=document.getElementById('qrMask');
  var img=document.getElementById('qrImg');
  open.onclick=function(){
    img.src='qr_quiz.png?t='+Date.now();   // 服务重启后 IP 可能变，强制刷新
    mask.classList.add('on');
__URLFETCH__  };
  document.getElementById('qrClose').onclick=function(){mask.classList.remove('on');};
  mask.onclick=function(e){ if(e.target===mask) mask.classList.remove('on'); };
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape') mask.classList.remove('on');
  });
  document.getElementById('qrCopy').onclick=function(){
    var t=document.getElementById('qrUrl').textContent.trim();
    var b=this;
    function done(){ b.textContent='已复制'; setTimeout(function(){b.textContent='复制地址';},1200); }
    try{
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(t).then(done).catch(function(){prompt('复制地址：',t);});
      } else prompt('复制地址：',t);
    }catch(err){ prompt('复制地址：',t); }
  };
})();
</script>
</body></html>
"""


def main():
    summary = json.load(open(os.path.join(OUT, "data", "summary.json"), encoding="utf-8"))
    quiz = json.load(open(os.path.join(OUT, "data", "quiz.json"), encoding="utf-8"))
    bp = os.path.join(OUT, "data", "bigq.json")
    bigq = json.load(open(bp, encoding="utf-8")) if os.path.exists(bp) else []
    cp = os.path.join(OUT, "data", "connect.json")
    conn = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}

    n_brow = len([1])  # placeholder
    nq = summary["n_questions"]
    url = conn.get("quiz") or "http://<电脑IP>:8000/quiz.html"

    html = (TEMPLATE
            .replace("__CSS__", CSS)
            .replace("__NQ__", str(nq))
            .replace("__NBIG__", str(len(bigq)))
            .replace("__NSEL__", str(len(quiz)))
            .replace("__NKP__", str(len(summary["kps"])))
            .replace("__NY__", str(len(summary["years"])))
            .replace("__URL__", url)
            # 弹窗打开时实时读取当前地址，避免 IP 变了以后显示过期地址
            .replace("__URLFETCH__", (
                "  fetch('data/connect.json?t='+Date.now()).then(function(r){return r.json();})"
                "    .then(function(c){ if(c && c.quiz) document.getElementById('qrUrl').textContent=c.quiz; })"
                "    .catch(function(){});\n")))
    dest = os.path.join(OUT, "index.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {dest}  {len(html.encode('utf-8'))/1024:.1f} KB  "
          f"题 {nq} / 选择 {len(quiz)} / 综合 {len(bigq)} / 知识点 {len(summary['kps'])}")


if __name__ == "__main__":
    main()
