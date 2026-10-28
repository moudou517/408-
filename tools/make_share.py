# -*- coding: utf-8 -*-
"""
生成「发给他人的离线分享包」。

设计目标：
  * 对方电脑上什么都不用装（不要 Python、不要服务器、不要联网）
  * 整个目录可以随便改盘符 / 改名 / 压缩解压，双击就能用
  * 只带走真正需要的东西（不带 .pylibs / work / 原始 PDF）

产物:
  E:\\CST\\408\\分享\\408真题复习包\\        <- 目录
  E:\\CST\\408\\分享\\408真题复习包.zip      <- 直接发这个
"""
import os
import re
import sys
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'out')
SHARE = os.path.join(ROOT, '分享')
NAME = '408真题复习包'
DST = os.path.join(SHARE, NAME)

# 需要带走的顶层文件（相对 out/）
FILES = [
    'map.html',
    'browse.html',
    'quiz.html',
    'bigq.html',
    'report.html',
    '408_题库索引.pdf',
    '408_图表集.pdf',
    '408_真题分类与120分复习方案.md',
]
# 需要带走的目录
DIRS = ['qimg', 'fig']

ICO = os.path.join(ROOT, '408.ico')

README = u'''408 真题复习包 · 使用说明
========================================================

【怎么打开】
  双击本文件夹里的「双击这里开始复习.bat」。
  如果没反应 / 弹出安全警告 / 浏览器没动静 ——
  直接进 out 文件夹，双击 index.html，效果完全一样。
  （推荐用 Edge / Chrome / Safari 最新版打开）

【要装什么】
  什么都不用装。没有 Python、没有服务器、不用联网。
  题目、解析、插图、思维导图、分析报告全部内嵌在网页里，
  整个文件夹可以随便移动、复制、压缩、换盘符。

【里面有什么】
  out/index.html            总入口：知识体系 / 题库 / 刷题 三个门
  out/map.html              知识框架：4 科 → 章 → 116 个考点，
                            每个考点可一键跳进对应题库或看解析
  out/browse.html           题库全集：830 道真题，按科目/章/考点检索，带解析
  out/quiz.html             选择题刷题：686 道，8 种题库 × 2 种出题顺序 × 2 种判分
  out/bigq.html             综合题刷题：119 道，先自己写再看参考答案与思路
  out/report.html           完整分析报告：18 年真题分类 + 120 分复习方案 + 图表
  out/408_题库索引.pdf       打印版索引（66 页，PDF 内部可跳转）
  out/408_图表集.pdf         打印版图表（32 页）
  out/qimg/  out/fig/        题目插图 / 思维导图与流程图

【怎么用最省时间】
  1) 先看 map.html，把标了【必考】【高频】的考点过一遍；
  2) 每个考点后面点「刷选择」，错题自动进错题本；
  3) 综合题用 bigq.html，先自己在纸上写思路再点「显示参考答案」；
  4) 考前一周刷 index.html → 刷题 → 按年份顺序 × 交卷模式，整套模拟。

【几点说明】
  · 做题记录（对错、错题本、综合题会/不会）存在浏览器本地
    （localStorage），换电脑、换浏览器或清缓存会丢，这是正常的。
  · 手机/平板也能看，但小题插图在手机上偏小，还是电脑舒服。
  · 内容取自 2009–2026 共 18 套 408 真题及其官方解析，
    考点按 2025 考纲整理为 127 个叶子知识点；
    选择题可用解析 686/711（其余选项是图片，未收），
    综合题解析 116/119。
  · 全部为学习资料，请勿商用。

========================================================
如果想让桌面有个带图标的快捷方式：双击「创建桌面快捷方式.bat」。
（它按当前所在路径生成，所以整个文件夹搬走后重新双击一次即可。）
'''


def _read(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()


def _write(p, s, encoding='utf-8'):
    with open(p, 'w', encoding=encoding, newline='\n') as f:
        f.write(s)


def build_index(src_path, dst_path):
    """把 out/index.html 改造成离线版：去掉平板二维码入口。"""
    html = _read(src_path)
    n0 = len(html)

    # 1. 顶部「平板连接」按钮 -> 静态说明
    html = html.replace(
        '<button class="qrbtn" id="qrOpen">\U0001F4F1 平板连接</button>',
        '<span class="qrbtn" style="border:none;background:transparent;'
        'cursor:default;color:#8a7f72">离线版 · 无需联网</span>')

    # 2. 删掉二维码弹窗 + 它的脚本（两者在文件末尾连成一段）
    a = html.find('<div class="mask" id="qrMask">')
    if a != -1:
        b = html.rfind('</script>')
        b = (b + len('</script>')) if b != -1 else len(html)
        html = html[:a] + html[b:]

    # 3. 底部链接：connect.html / README.md 不在包里
    html = html.replace('\n      <a href="connect.html">平板连接说明</a>', '')
    html = html.replace('<a href="README.md">交付说明</a>',
                        '<a href="../使用说明.txt">使用说明</a>')

    # 4. 页脚写死的本地路径 + 面向他人的措辞
    html = html.replace('答案与解析取自你提供的各年《真题解析》',
                        '答案与解析取自各年《408 真题解析》')
    html = html.replace('原件：E:\\CST\\408\\out\\',
                        '离线版：全部内容已内嵌，无需联网、无需安装')

    assert 'qrMask' not in html, '二维码弹窗没删干净'
    assert 'connect.json' not in html, 'connect.json 引用没删干净'
    assert '</html>' in html, 'html 结尾丢了'
    _write(dst_path, html)
    return n0, len(html)


# ---------------------------------------------------------------- 启动脚本
BAT_OPEN = u'''@echo off
chcp 936 >nul
title 408 真题复习中心
setlocal
set "ROOT=%~dp0"
if exist "%ROOT%out\\index.html" (
    start "" "%ROOT%out\\index.html"
) else (
    echo.
    echo   [提示] 没找到 out\\index.html
    echo   请确认本 bat 和 out 文件夹在同一个目录里。
    echo.
    pause
)
endlocal
'''

BAT_LNK = u'''@echo off
chcp 936 >nul
setlocal
set "ROOT=%~dp0"
echo 正在按当前路径创建桌面快捷方式...
echo   目标: %ROOT%双击这里开始复习.bat
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$w=New-Object -ComObject WScript.Shell; $d=[Environment]::GetFolderPath('Desktop'); $s=$w.CreateShortcut($d+'\\408 真题复习中心.lnk'); $s.TargetPath='%ROOT%双击这里开始复习.bat'; $s.WorkingDirectory='%ROOT%'; if(Test-Path '%ROOT%408.ico'){$s.IconLocation='%ROOT%408.ico'}; $s.Description='408 真题复习 · 知识体系/题库/刷题'; $s.Save(); Write-Host ('已创建: '+$d+'\\408 真题复习中心.lnk')"
echo.
pause
endlocal
'''


def main():
    if not os.path.isdir(SRC):
        sys.exit('找不到 out 目录: %s' % SRC)
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    os.makedirs(os.path.join(DST, 'out'))

    od = os.path.join(DST, 'out')
    missing = []
    for f in FILES:
        s = os.path.join(SRC, f)
        if not os.path.exists(s):
            missing.append(f)
            continue
        shutil.copy2(s, os.path.join(od, f))
    for d in DIRS:
        s = os.path.join(SRC, d)
        if not os.path.isdir(s):
            missing.append(d + '/')
            continue
        shutil.copytree(s, os.path.join(od, d))
    if missing:
        print('[warn] 缺少:', ', '.join(missing))

    n0, n1 = build_index(os.path.join(SRC, 'index.html'),
                         os.path.join(od, 'index.html'))

    if os.path.exists(ICO):
        shutil.copy2(ICO, os.path.join(DST, '408.ico'))

    _write(os.path.join(DST, '双击这里开始复习.bat'), BAT_OPEN, 'gbk')
    _write(os.path.join(DST, '创建桌面快捷方式.bat'), BAT_LNK, 'gbk')
    _write(os.path.join(DST, '使用说明.txt'), README, 'utf-8-sig')

    # ------------------------------------------------ 自检：本地链接是否都在
    bad = []
    for name in sorted(os.listdir(od)):
        if not name.endswith('.html'):
            continue
        p = os.path.join(od, name)
        html = _read(p)
        for m in re.finditer(r'(?:href|src)\s*=\s*"([^"]+)"', html):
            u = m.group(1).split('?')[0].split('#')[0]
            if not u or u.startswith(('http:', 'https:', 'data:', 'mailto:',
                                      'javascript:', '//')):
                continue
            target = os.path.join(od, u.replace('/', os.sep))
            if not os.path.exists(target):
                bad.append('%s -> %s' % (name, u))

    # ------------------------------------------------ 打包
    zip_path = os.path.join(SHARE, NAME + '.zip')
    if os.path.exists(zip_path):
        os.remove(zip_path)
    nfile = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED,
                         compresslevel=4) as z:
        for base, _dirs, files in os.walk(DST):
            for fn in files:
                full = os.path.join(base, fn)
                rel = os.path.relpath(full, SHARE)
                z.write(full, rel)
                nfile += 1

    total = sum(os.path.getsize(os.path.join(b, f))
                for b, _d, fs in os.walk(DST) for f in fs)
    print('')
    print('包的目录 : %s' % DST)
    print('压缩包   : %s' % zip_path)
    print('文件数   : %d  目录 %.1f MB  压缩后 %.1f MB'
          % (nfile, total / 1048576.0, os.path.getsize(zip_path) / 1048576.0))
    print('index.html: %.1f KB -> %.1f KB' % (n0 / 1024.0, n1 / 1024.0))
    print('本地链接缺失: %d' % len(bad))
    for b in bad[:20]:
        print('   ' + b)


if __name__ == '__main__':
    main()
