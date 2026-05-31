@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title AI饮食健康助手

echo.
echo  ============================================
echo    🥗  AI饮食健康助手 - 一键启动
echo  ============================================
echo.

REM ---------- 自动检测 Python ----------
echo  [1/4] 检测 Python...
set PYTHON_CMD=
for %%p in (python python3 py) do (
    where %%p >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%v in ('%%p --version 2^>^&1') do echo  ✅ %%v
        set PYTHON_CMD=%%p
        goto :python_found
    )
)
echo  ❌ 未检测到 Python，请安装 Python 3.10+
pause
exit /b 1

:python_found

REM ---------- 自动检测 Node ----------
echo  [2/4] 检测 Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo  ❌ 未检测到 Node.js，请安装 Node.js 18+
    pause
    exit /b 1
)
for /f "tokens=1 delims=v" %%v in ('node --version 2^>^&1') do echo  ✅ Node.js v%%v

REM ---------- 首次安装后端依赖 ----------
echo  [3/4] 检查后端依赖...
cd /d "%~dp0backend"
call %PYTHON_CMD% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
echo  ✅ 后端依赖就绪

REM ---------- 首次安装前端依赖 ----------
echo  [4/4] 检查前端依赖...
cd /d "%~dp0frontend"
if not exist "node_modules\" call npm install --registry https://registry.npmmirror.com
echo  ✅ 前端依赖就绪

echo.
echo  ============================================
echo    🚀 启动服务（后台运行）
echo  ============================================
echo.
echo   后端 API:  http://localhost:8000
echo   前端页面:  http://localhost:5173
echo   API 文档:  http://localhost:8000/docs
echo.

REM ---------- 杀掉旧进程 ----------
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM ---------- 启动后端（不用--reload，更稳定）----------
cd /d "%~dp0backend"
start /min "" %PYTHON_CMD% -m uvicorn app.main:app --host 0.0.0.0 --port 8000

REM ---------- 启动前端 ----------
cd /d "%~dp0frontend"
start /min "" cmd /c "npx vite --host"

echo.
echo  ✅ 服务已启动！等待3秒后打开浏览器...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo  ⚠️ 服务在后台运行，关闭此窗口不影响使用。
echo  ⚠️ 如需停止服务，重新运行此脚本即可。
echo.
pause
