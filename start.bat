@echo off
chcp 65001 > nul
title 每周一山 · 本地开发服务

echo ============================================================
echo   🏔️ 每周一山 · 成都周边50座山 · 攻略手册
echo   🚀 正在启动本地开发服务...
echo ============================================================
echo.

cd /d "%~dp0"

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js / npm 环境，请先安装 Node.js。
    echo.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [提示] 首次运行，正在自动安装依赖 (npm install)...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络环境。
        pause
        exit /b 1
    )
)

echo [提示] 启动成功后，会自动在默认浏览器打开。
echo [提示] 局域网内其他设备/手机可通过局域网 IP:5173 访问测试。
echo [提示] 如需停止服务，请直接关闭本窗口或按 Ctrl + C。
echo.

call npm run dev -- --host --open

if %errorlevel% neq 0 (
    echo.
    echo [错误] 服务已退出或发生错误。
    pause
)
