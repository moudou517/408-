# -*- coding: utf-8 -*-
"""One-click launcher for the 408 review materials.

用法:
    pythonw launch.py [页面] [--folder]

  pythonw launch.py quiz.html      # 起服务并打开刷题页（默认）
  pythonw launch.py index.html     # 起服务并打开资料入口
  pythonw launch.py --folder       # 直接在资源管理器打开资料目录

行为：
  * 8000 端口已经在跑本地服务 -> 直接复用，不重复启动
  * 端口被别的程序占用 -> 自动改用 8010/8020/8030
  * 服务未启动 -> 后台分离启动 serve.py，等它就绪后再打开浏览器
"""

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROOT = os.path.abspath(ROOT)
OUT = os.path.join(ROOT, "out")
SERVE = os.path.join(ROOT, "tools", "serve.py")
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


def port_open(port, host="127.0.0.1", timeout=0.35):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0


def is_our_server(port):
    """确认端口上跑的是本资料的静态服务，而不是别的程序。"""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/data/quiz.json",
                                    timeout=1.5) as r:
            data = json.loads(r.read().decode("utf-8"))
        return isinstance(data, list) and len(data) > 0 and "op" in data[0]
    except Exception:
        return False


def start_server(port):
    py = sys.executable
    if py.lower().endswith("pythonw.exe"):
        py = py[:-len("pythonw.exe")] + "python.exe"
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.Popen(
        [py, SERVE, str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        env=env,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
    )


def pick_port(candidates=(8000, 8010, 8020, 8030)):
    for p in candidates:
        if not port_open(p):
            start_server(p)
            for _ in range(60):
                time.sleep(0.25)
                if port_open(p):
                    return p
            continue
        if is_our_server(p):
            return p
    return None


def main():
    args = [a for a in sys.argv[1:] if a]
    if args and args[0] in ("--folder", "-f"):
        subprocess.Popen(["explorer", OUT])
        return 0
    page = args[0] if args else "quiz.html"
    port = pick_port()
    if port is None:
        subprocess.Popen(["explorer", OUT])
        return 1
    url = f"http://127.0.0.1:{port}/{page}"
    webbrowser.open(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
