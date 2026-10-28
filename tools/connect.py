# -*- coding: utf-8 -*-
"""Print the tablet connection info, render QR codes and a connect.html card.

平板输入网址这件事能省则省：这里生成二维码（扫码直达），同时把 IP / 端口 / 主机名
都写清楚。每次服务启动都会重跑一遍，所以 IP 变了二维码也跟着变。
"""

import json
import os
import socket
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROOT = os.path.abspath(ROOT)
OUT = os.path.join(ROOT, "out")
DEFAULT_PORT = 8000


def primary_ip():
    """默认路由所用网卡的 IP（UDP connect 不会真的发包）。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        return "127.0.0.1"


def candidate_ips():
    ips = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127.") or ip.startswith("169.254."):
                continue
            if ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    p = primary_ip()
    if p in ips:
        ips.remove(p)
    return [p] + ips


def make_qr(url, dest):
    try:
        import qrcode
        from qrcode.image.pil import PilImage
    except Exception as e:
        print(f"  (qrcode 不可用: {e})")
        return None
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1613", back_color="#ffffff").convert("RGB")
    img = img.resize((520, 520), resample=0)
    img.save(dest)
    return dest


CONNECT_CSS = """
:root{--paper:#f6f2e9;--panel:#fcfaf5;--ink:#1a1613;--ink2:#4a423a;--ink3:#8a7f72;
 --rule:#e0d8c9;--rule2:#cfc4b0;--acc:#1f5fa8;
 --serif:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",Georgia,serif;
 --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Segoe UI",sans-serif;
 --mono:"Cascadia Mono",Consolas,"Courier New",monospace;}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
 font-size:15px;line-height:1.75;
 background-image:radial-gradient(rgba(160,140,110,.06) 1px,transparent 1px);background-size:3px 3px;}
.wrap{max-width:900px;margin:0 auto;padding:34px 24px 80px}
.kicker{font-family:var(--mono);font-size:10.5px;letter-spacing:2px;color:var(--ink3);margin-bottom:8px}
h1{font-family:var(--serif);font-size:28px;font-weight:600;margin:0 0 6px;letter-spacing:.6px}
.lede{color:var(--ink2);font-size:13.6px;margin:0 0 24px}
.grid{display:grid;grid-template-columns:auto 1fr;gap:28px;align-items:start;
 background:var(--panel);border:1px solid var(--rule);padding:26px;border-radius:6px}
.qr{text-align:center}
.qr img{width:250px;height:250px;display:block;border:1px solid var(--rule);background:#fff}
.qr p{font-size:11.5px;color:var(--ink3);margin:8px 0 0;font-family:var(--mono)}
.urlbox{margin:0 0 16px}
.urlbox label{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:1.4px;
 color:var(--ink3);text-transform:uppercase;margin-bottom:4px}
.url{font-family:var(--mono);font-size:20px;color:var(--ink);background:#fff;
 border:1px solid var(--rule2);border-radius:4px;padding:11px 14px;display:block;
 letter-spacing:.5px;user-select:all;word-break:break-all}
.url.small{font-size:15px;padding:8px 12px;color:var(--ink2)}
.facts{display:flex;gap:22px;flex-wrap:wrap;margin:18px 0 0;font-size:13px;color:var(--ink2)}
.facts div b{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:1.2px;
 color:var(--ink3);text-transform:uppercase;margin-bottom:2px;font-weight:400}
h2{font-family:var(--serif);font-size:17px;font-weight:600;margin:30px 0 8px}
ol,ul{margin:8px 0 8px 20px;padding:0}
li{margin:5px 0;font-size:13.8px;color:var(--ink2)}
code{font-family:var(--mono);background:#efe9db;padding:1px 6px;border-radius:3px;font-size:12.6px}
.warn{background:#fff6e5;border:1px solid #f0d3a8;border-radius:4px;padding:12px 16px;
 font-size:13.4px;color:#7a4d05;margin:14px 0}
.note{font-size:12.5px;color:var(--ink3);margin-top:26px;font-family:var(--mono)}
a{color:var(--acc)}
@media (max-width:720px){.grid{grid-template-columns:1fr}.qr img{margin:0 auto}}
@media print{body{background:#fff}}
"""


def write_connect_html(ip, port, host):
    quiz = f"http://{ip}:{port}/quiz.html"
    home = f"http://{ip}:{port}/"
    by_host = f"http://{host}:{port}/" if host else ""
    html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>平板连接 · 408 复习资料</title><style>{CONNECT_CSS}</style></head><body>
<div class="wrap">
  <div class="kicker">CONNECT / 408</div>
  <h1>用平板连接这台电脑</h1>
  <p class="lede">平板和电脑连同一个 Wi-Fi，然后在平板浏览器里输入下面的地址。或者——直接扫右边的二维码，不用打字。</p>

  <div class="grid">
    <div class="qr">
      <img src="qr_quiz.png" alt="扫码打开刷题页">
      <p>扫码直达刷题</p>
    </div>
    <div>
      <div class="urlbox">
        <label>刷题（推荐）</label>
        <span class="url">{quiz}</span>
      </div>
      <div class="urlbox">
        <label>资料入口页</label>
        <span class="url small">{home}</span>
      </div>
      {f'<div class="urlbox"><label>用主机名（IP 变了也能用）</label><span class="url small">{by_host}</span></div>' if by_host else ''}
      <div class="facts">
        <div><b>IP</b>{ip}</div>
        <div><b>端口</b>{port}</div>
        <div><b>电脑名</b>{host or '-'}</div>
      </div>
    </div>
  </div>

  <h2>连不上？按顺序检查这四条</h2>
  <ol>
    <li><b>同一个 Wi-Fi。</b>平板别连成 5G/访客网络以外的别的网段，也别用蜂窝数据。</li>
    <li><b>电脑上的服务窗口还开着。</b>用 <code>快捷方式\\启动局域网服务_平板用.bat</code> 启动，
        窗口里会列出全部可用地址；关掉窗口服务就停了。</li>
    <li><b>防火墙放行。</b>双击 <code>快捷方式\\允许平板访问_加防火墙规则.bat</code>（会弹 UAC，点是）。
        这是最常见的原因。</li>
    <li><b>地址抄对了。</b>只填 <code>{ip}:{port}</code>，前面加 <code>http://</code>，
        注意是<b>冒号</b>不是斜杠。</li>
  </ol>

  <div class="warn">
    安全提示：这个服务没有密码，同一局域网内任何人都能访问。只在自家的 Wi-Fi 下开，
    在公共网络（图书馆、咖啡店）里用完记得关掉服务窗口。
  </div>

  <p class="note">本页由 tools/connect.py 自动生成 · 每次启动服务都会刷新 IP 与二维码</p>
</div></body></html>"""
    dest = os.path.join(OUT, "connect.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    return dest


def main(port=None):
    if port is None:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    port = int(port)
    host = socket.gethostname()
    ips = candidate_ips()
    ip = ips[0] if ips else "127.0.0.1"

    quiz = f"http://{ip}:{port}/quiz.html"
    qr = make_qr(quiz, os.path.join(OUT, "qr_quiz.png"))
    make_qr(f"http://{ip}:{port}/", os.path.join(OUT, "qr_index.png"))
    page = write_connect_html(ip, port, host)
    json.dump({"ip": ip, "port": port, "host": host,
               "quiz": quiz, "home": f"http://{ip}:{port}/",
               "all_ips": ips},
              open(os.path.join(OUT, "data", "connect.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    line = "=" * 62
    print(line)
    print("  408 复习资料 —— 平板连接地址")
    print(line)
    print(f"  刷题      {quiz}")
    print(f"  资料入口  http://{ip}:{port}/")
    print(f"  主机名    http://{host}:{port}/")
    if len(ips) > 1:
        print("  其它网卡  " + "  ".join(f"http://{x}:{port}/" for x in ips[1:]))
    print(f"  二维码    {os.path.join(OUT, 'connect.html')}  （电脑上打开可扫码）")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
