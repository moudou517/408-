# -*- coding: utf-8 -*-
"""校验一个「离线分享包」目录是否自洽（可以放到任何路径/任何电脑上直接用）。

用法:
    python tools/verify_share.py "C:\\Temp\\x\\408真题复习包"

检查项:
  1. 必需文件/目录是否齐全
  2. 所有 html 里的 href/src 相对引用是否都能落到真实文件（跳过 JS 模板串）
  3. 是否还残留绝对路径（E:\\CST、盘符路径、127.0.0.1、data/connect.json）
  4. bat 能否按 GBK 解码、关键语句是否在
  5. 图片总数 / 总大小
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

REQUIRED = ['out/index.html', 'out/map.html', 'out/browse.html', 'out/quiz.html',
            'out/bigq.html', 'out/report.html', 'out/qimg', 'out/fig',
            '使用说明.txt', '双击这里开始复习.bat']
BAD_PAT = [
    (r'E:\\CST', 'Windows 绝对路径 E:\\CST'),
    (r'[A-Za-z]:\\(?:CST|408)', '盘符绝对路径'),
    (r'127\.0\.0\.1:\d+', 'localhost 地址'),
    (r'data/connect\.json', 'connect.json 引用'),
    (r'qrMask', '平板二维码弹窗'),
]
LOCAL_PREFIX = ('http:', 'https:', 'data:', 'mailto:', 'javascript:', '//', '#')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}


class Balance(HTMLParser):
    """不依赖浏览器的结构检查：标签是否配平、payload JSON 是否可解析。"""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.stack = []
        self.err = []
        self.payload = None
        self._in_payload = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script' and a.get('id') == 'payload':
            self._in_payload = True
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, data):
        if self._in_payload:
            self.payload = (self.payload or '') + data

    def handle_endtag(self, tag):
        if tag == 'script':
            self._in_payload = False
        if tag in VOID:
            return
        if not self.stack:
            self.err.append('多余的 </%s>' % tag)
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            # 容错：向上找最近的同名标签
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i] == tag:
                    self.err.append('</%s> 之前未闭合: %s'
                                    % (tag, ','.join(self.stack[i + 1:])))
                    del self.stack[i:]
                    return
            self.err.append('多余的 </%s>' % tag)


def check(root):
    ok, bad = [], []

    for r in REQUIRED:
        p = os.path.join(root, r.replace('/', os.sep))
        if os.path.exists(p):
            ok.append('存在: ' + r)
        else:
            bad.append('缺失: ' + r)

    # ---- html 引用
    nref = 0
    od = os.path.join(root, 'out')
    for fn in sorted(os.listdir(od)):
        if not fn.endswith('.html'):
            continue
        with open(os.path.join(od, fn), encoding='utf-8') as f:
            html = f.read()
        for m in re.finditer(r'(?:href|src)\s*=\s*"([^"]+)"', html):
            u = m.group(1)
            if u.startswith(LOCAL_PREFIX) or '$' in u or "'" in u or '+' in u:
                continue          # 外链 / JS 模板串
            nref += 1
            u = u.split('?')[0].split('#')[0]
            if not u:
                continue
            t = os.path.join(od, u.replace('/', os.sep))
            if not os.path.exists(t):
                bad.append('%s -> %s' % (fn, u))
        for pat, why in BAD_PAT:
            if re.search(pat, html):
                bad.append('%s 残留: %s' % (fn, why))

        b = Balance()
        try:
            b.feed(html)
            b.close()
        except Exception as e:                      # pragma: no cover
            bad.append('%s 解析失败: %s' % (fn, e))
            continue
        for e in b.err[:4]:
            bad.append('%s 结构: %s' % (fn, e))
        if b.stack:
            bad.append('%s 未闭合标签: %s' % (fn, ','.join(b.stack[:6])))
        if b.payload:
            try:
                d = json.loads(b.payload)
                rows = d.get('rows') if isinstance(d, dict) else d
                if rows is None:
                    rows = [d]
                ok.append('%s 内嵌数据 %d 项' % (fn, len(rows)))
            except Exception as e:
                bad.append('%s 内嵌 JSON 坏了: %s' % (fn, e))
    ok.append('html 相对引用 %d 条全部命中' % nref)

    # ---- bat
    for fn in ('双击这里开始复习.bat', '创建桌面快捷方式.bat'):
        p = os.path.join(root, fn)
        if not os.path.exists(p):
            continue
        raw = open(p, 'rb').read()
        try:
            txt = raw.decode('gbk')
        except UnicodeDecodeError:
            bad.append(fn + ' 不是合法 GBK')
            continue
        if '%~dp0' not in txt:
            bad.append(fn + ' 没用 %~dp0（搬走会失效）')
        if re.search(r'[A-Za-z]:\\', txt):
            bad.append(fn + ' 里还有盘符绝对路径')
        ok.append(fn + ' GBK / %~dp0 正常')

    # ---- 体量
    imgs = 0
    total = 0
    for base, _d, files in os.walk(root):
        for f in files:
            total += os.path.getsize(os.path.join(base, f))
            if f.lower().endswith(('.png', '.jpg', '.gif')):
                imgs += 1
    ok.append('图片 %d 张 / 总计 %.1f MB' % (imgs, total / 1048576.0))
    return ok, bad


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    root = os.path.abspath(root)
    print('校验目录: %s' % root)
    ok, bad = check(root)
    for s in ok:
        print('  [OK] ' + s)
    for s in bad:
        print('  [!!] ' + s)
    print('')
    print('结果: %s（问题 %d 项）' % ('通过' if not bad else '有问题', len(bad)))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
