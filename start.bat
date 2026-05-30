@echo off
chcp 65001 >nul
title AI饮食健康助手 - 启动中...

set PYTHON_PATH=C:\Users\hgdcy\AppData\Local\Programs\Python\Python313\python.exe
set NODE_PATH=F:\nodejs\extracted\node-v22.15.0-win-x64
set PATH=%NODE_PATH%;%PATH%

echo.
echo  ============================================
echo   🥗  AI饮食健康助手 - 一键启动
echo  ============================================
echo.

REM ---------- 检查 Python ----------
echo  [1/4] 检查 Python...
"%PYTHON_PATH%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ❌ 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('"%PYTHON_PATH%" --version 2^>^&1') do echo  ✅ Python %%v

REM ---------- 检查 Node.js ----------
echo  [2/4] 检查 Node.js...
"%NODE_PATH%\node.exe" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ❌ 未检测到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)
for /f "tokens=1 delims=v" %%v in ('"%NODE_PATH%\node.exe" --version 2^>^&1') do echo  ✅ Node.js %%v

REM ---------- 安装后端依赖 ----------
echo  [3/4] 安装后端依赖...
cd /d "%~dp0backend"
"%PYTHON_PATH%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

REM ---------- 安装前端依赖 ----------
echo  [4/4] 安装前端依赖...
cd /d "%~dp0frontend"
if not exist "node_modules\" (
    "%NODE_PATH%\npm.cmd" install --registry https://registry.npmmirror.com
)

echo.
echo  ============================================
echo   🚀 启动服务...
echo  ============================================
echo.
echo   后端 API:  http://localhost:8000
echo   前端页面:  http://localhost:5173
echo   API 文档:  http://localhost:8000/docs
echo.
echo   按 Ctrl+C 停止所有服务
echo  ============================================
echo.

REM ---------- 启动后端 ----------
cd /d "%~dp0backend"
start "AI饮食-后端" cmd /c ""%PYTHON_PATH%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM ---------- 启动前端 ----------
cd /d "%~dp0frontend"
start "AI饮食-前端" cmd /c ""%NODE_PATH%\npm.cmd" run dev"

echo ✅ 两个服务已启动，正在打开浏览器...
timeout /t 3 /nobreak >nul
start http://localhost:5173

cd /d "%~dp0"
pause
