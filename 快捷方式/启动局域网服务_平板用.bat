@echo off
chcp 936 >nul
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
title 408 复习资料 - 局域网服务（平板用）
set "PYC=D:\Python\python.exe"
if not exist "%PYC%" set "PYC="
if not defined PYC for %%X in (python.exe) do if not "%%~$PATH:X"=="" set "PYC=%%~$PATH:X"
if not defined PYC (
    echo [错误] 没找到 python.exe，平板模式需要先装 Python 3。
    echo        只在自己电脑上看的话，直接双击 out\index.html 就够了。
    echo.
    pause
    exit /b 1
)
set "PYTHONPATH=%ROOT%\.pylibs"
set "PYTHONIOENCODING=utf-8"
echo ============================================================
echo   408 复习资料 - 局域网服务
echo   保持本窗口开着，关掉窗口服务就停了。
echo   平板 / 手机连同一个 Wi-Fi，用下面的地址访问。
echo ============================================================
echo.
"%PYC%" "%ROOT%\tools\serve.py" 8000
echo.
echo 服务已停止。
pause
endlocal
