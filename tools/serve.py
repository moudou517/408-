"""Static file server for the 408 materials, with LAN connection info on startup.

Exposes ../out to the LAN so a tablet can open the quiz/report by URL or QR code.
"""

import functools
import http.server
import os
import socket
import socketserver
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))
        sys.stderr.flush()

    def end_headers(self):
        # 平板浏览器缓存中文文件名时不至于乱码
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def announce():
    """刷新二维码/连接页并打印地址（IP 变了这里会跟着变）。"""
    print(f"SERVING {ROOT}", flush=True)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import connect
        connect.main(PORT)          # 生成 qr_quiz.png / connect.html / connect.json + 打印地址
        return
    except Exception as e:
        print(f"(连接信息生成失败: {type(e).__name__}: {e})", flush=True)

    print(f"LOCAL   http://127.0.0.1:{PORT}/", flush=True)
    for ip in sorted({i[4][0] for i in socket.getaddrinfo(
            socket.gethostname(), None, socket.AF_INET)}):
        print(f"LAN     http://{ip}:{PORT}/", flush=True)


def main():
    handler = functools.partial(Handler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), handler) as httpd:
        announce()
        print("PRESS CTRL+C TO STOP", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
