# 创建 408 复习中心的一键快捷方式（单个入口）
# 用法:  pwsh -File make_shortcuts.ps1 -Dest "C:\Users\xxx\Desktop"

param(
  [string]$Dest = "",
  [string]$Root = "E:\CST\408"
)

$ErrorActionPreference = "Stop"
$pyw = "D:\Python\pythonw.exe"
if (-not (Test-Path $pyw)) { $pyw = (Get-Command pythonw -ErrorAction SilentlyContinue).Source }
if (-not $pyw) { throw "找不到 pythonw.exe" }

$launcher = Join-Path $Root "tools\launch.py"
$icon     = Join-Path $Root "408.ico"

function New-Lnk([string]$dir, [string]$name, [string]$args_, [string]$desc) {
  $path = Join-Path $dir ($name + ".lnk")
  $sh = New-Object -ComObject WScript.Shell
  $sc = $sh.CreateShortcut($path)
  $sc.TargetPath       = $pyw
  $sc.Arguments        = $args_
  $sc.WorkingDirectory = $Root
  $sc.Description      = $desc
  $sc.IconLocation     = "$icon,0"
  $sc.WindowStyle      = 7
  $sc.Save()
  return $path
}

"pythonw : $pyw"
$made = @()

# 唯一入口：408 复习中心（进去再选 知识体系 / 题库 / 刷题）
$localDir = Join-Path $Root "快捷方式"
New-Item -ItemType Directory -Force -Path $localDir | Out-Null
$made += New-Lnk $localDir "408 复习中心" "`"$launcher`" index.html" `
  "打开 408 复习中心（知识体系 / 题库 / 刷题 / 平板连接）"

# 兜底批处理
$bats = @(
  @{ f = "打开复习中心.bat"; a = "index.html" },
  @{ f = "直接刷选择题.bat"; a = "quiz.html" },
  @{ f = "直接刷综合题.bat"; a = "bigq.html" },
  @{ f = "打开知识体系.bat"; a = "map.html" },
  @{ f = "打开题库.bat";     a = "browse.html" }
)
foreach ($b in $bats) {
  $line = "@echo off`r`nstart `"`" `"$pyw`" `"$launcher`" $($b.a)`r`n"
  Set-Content -Path (Join-Path $localDir $b.f) -Value $line -Encoding Default
}

# 桌面：只放一个，并清理旧的多入口快捷方式
if ($Dest -and (Test-Path $Dest)) {
  $legacy = @("408 刷题", "408 复习资料", "408 平板连接", "408 资料文件夹", "408 复习中心")
  foreach ($n in $legacy) {
    $p = Join-Path $Dest ($n + ".lnk")
    if (Test-Path $p) { Remove-Item $p -Force; "  removed  $n.lnk" }
  }
  $made += New-Lnk $Dest "408 复习中心" "`"$launcher`" index.html" `
    "打开 408 复习中心（知识体系 / 题库 / 刷题 / 平板连接）"
} elseif ($Dest) {
  Write-Warning "目标目录不存在: $Dest"
}

"--- 已创建 ---"
$made | ForEach-Object { "  $_" }
"--- 快捷方式目录 ---"
Get-ChildItem $localDir | ForEach-Object { "  $($_.Name)" }
