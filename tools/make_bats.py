# -*- coding: utf-8 -*-
"""重写「快捷方式」目录里的 bat，全部改成**相对路径**。

原来的 bat 把 E:\\CST\\408 和 D:\\Python\\pythonw.exe 写死了：
把文件夹复制到别的盘 / 别的电脑，双击就报
「快捷方式指向的驱动器或网络连接不可用」。
这里改成从 %~dp0 自推目录 + 自动找 python，搬到哪都能用。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, '快捷方式')

PY_FIND = r'''set "PYW=D:\Python\pythonw.exe"
if not exist "%PYW%" set "PYW="
if not defined PYW if exist "%ROOT%\.python_path" set /p PYW=<"%ROOT%\.python_path"
if not defined PYW for %%X in (pythonw.exe) do if not "%%~$PATH:X"=="" set "PYW=%%~$PATH:X"
if not defined PYW set "PYW=pythonw"
'''

HEAD = r'''@echo off
chcp 936 >nul
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
'''

PAGES = [
    ('打开复习中心.bat', 'index.html', '408 真题复习中心'),
    ('直接刷选择题.bat', 'quiz.html', '408 选择题刷题'),
    ('直接刷综合题.bat', 'bigq.html', '408 综合题刷题'),
    ('打开知识体系.bat', 'map.html', '408 知识体系'),
    ('打开题库.bat', 'browse.html', '408 题库'),
]

SERVE = u'''@echo off
chcp 936 >nul
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
title 408 复习资料 - 局域网服务（平板用）
set "PYC=D:\\Python\\python.exe"
if not exist "%PYC%" set "PYC="
if not defined PYC for %%X in (python.exe) do if not "%%~$PATH:X"=="" set "PYC=%%~$PATH:X"
if not defined PYC (
    echo [错误] 没找到 python.exe，平板模式需要先装 Python 3。
    echo        只在自己电脑上看的话，直接双击 out\\index.html 就够了。
    echo.
    pause
    exit /b 1
)
set "PYTHONPATH=%ROOT%\\.pylibs"
set "PYTHONIOENCODING=utf-8"
echo ============================================================
echo   408 复习资料 - 局域网服务
echo   保持本窗口开着，关掉窗口服务就停了。
echo   平板 / 手机连同一个 Wi-Fi，用下面的地址访问。
echo ============================================================
echo.
"%PYC%" "%ROOT%\\tools\\serve.py" 8000
echo.
echo 服务已停止。
pause
endlocal
'''

LNK = u'''@echo off
chcp 936 >nul
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
echo 按当前路径重建桌面快捷方式...
echo   目录: %ROOT%
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$w=New-Object -ComObject WScript.Shell; $d=[Environment]::GetFolderPath('Desktop'); $s=$w.CreateShortcut($d+'\\408 复习中心.lnk'); $s.TargetPath='%ROOT%\\快捷方式\\打开复习中心.bat'; $s.WorkingDirectory='%ROOT%'; if(Test-Path '%ROOT%\\408.ico'){$s.IconLocation='%ROOT%\\408.ico'}; $s.Description='408 真题复习 · 知识体系/题库/刷题/平板连接'; $s.Save(); Write-Host ('OK -> '+$d+'\\408 复习中心.lnk')"
echo.
pause
endlocal
'''


def main():
    os.makedirs(DIR, exist_ok=True)
    n = 0
    for fn, page, title in PAGES:
        body = (HEAD + 'title ' + title + '\n' + PY_FIND +
                'if not exist "%ROOT%\\tools\\launch.py" (\n'
                '    echo [错误] 找不到 tools\\launch.py，请确认整个 408 文件夹是完整的。\n'
                '    pause\n'
                '    exit /b 1\n'
                ')\n'
                'start "" "%PYW%" "%ROOT%\\tools\\launch.py" ' + page + '\n'
                'endlocal\n')
        with open(os.path.join(DIR, fn), 'w', encoding='gbk', newline='\r\n') as f:
            f.write(body)
        n += 1
    for fn, body in [('启动局域网服务_平板用.bat', SERVE),
                     ('创建桌面快捷方式.bat', LNK)]:
        with open(os.path.join(DIR, fn), 'w', encoding='gbk', newline='\r\n') as f:
            f.write(body)
        n += 1
    print('已重写 %d 个 bat: %s' % (n, DIR))
    for fn in sorted(os.listdir(DIR)):
        print('   %-34s %6d B' % (fn, os.path.getsize(os.path.join(DIR, fn))))


if __name__ == '__main__':
    main()
