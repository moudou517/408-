@echo off
chcp 936 >nul
title 放行端口 8000（让平板能访问）
echo ============================================================
echo   给"408 复习资料"开一个防火墙入站规则
echo ============================================================
echo.
echo 将在 Windows 防火墙中添加规则：
echo   名称：408复习资料 端口8000
echo   方向：入站   协议：TCP   端口：8000   动作：允许
echo.
echo 需要管理员权限，稍后会弹出 UAC 确认框，请点"是"。
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在申请管理员权限...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

netsh advfirewall firewall delete rule name="408复习资料 端口8000" >nul 2>&1
netsh advfirewall firewall add rule name="408复习资料 端口8000" dir=in action=allow protocol=TCP localport=8000 profile=private,domain
if %errorlevel% equ 0 (
    echo.
    echo [成功] 已放行 TCP 8000（仅专用/域网络）。
    echo        现在平板连同一 Wi-Fi，访问 电脑IP:8000 即可。
) else (
    echo.
    echo [失败] 添加规则失败，请检查是否点了 UAC 的"是"。
)
echo.
echo 按任意键关闭...
pause >nul
