@echo off
chcp 936 >nul
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
echo 按当前路径重建桌面快捷方式...
echo   目录: %ROOT%
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$w=New-Object -ComObject WScript.Shell; $d=[Environment]::GetFolderPath('Desktop'); $s=$w.CreateShortcut($d+'\408 复习中心.lnk'); $s.TargetPath='%ROOT%\快捷方式\打开复习中心.bat'; $s.WorkingDirectory='%ROOT%'; if(Test-Path '%ROOT%\408.ico'){$s.IconLocation='%ROOT%\408.ico'}; $s.Description='408 真题复习 · 知识体系/题库/刷题/平板连接'; $s.Save(); Write-Host ('OK -> '+$d+'\408 复习中心.lnk')"
echo.
pause
endlocal
