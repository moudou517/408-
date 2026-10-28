@echo off
chcp 936 >nul
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
title 408 知识体系
set "PYW=D:\Python\pythonw.exe"
if not exist "%PYW%" set "PYW="
if not defined PYW if exist "%ROOT%\.python_path" set /p PYW=<"%ROOT%\.python_path"
if not defined PYW for %%X in (pythonw.exe) do if not "%%~$PATH:X"=="" set "PYW=%%~$PATH:X"
if not defined PYW set "PYW=pythonw"
if not exist "%ROOT%\tools\launch.py" (
    echo [错误] 找不到 tools\launch.py，请确认整个 408 文件夹是完整的。
    pause
    exit /b 1
)
start "" "%PYW%" "%ROOT%\tools\launch.py" map.html
endlocal
