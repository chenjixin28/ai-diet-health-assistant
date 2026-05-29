@echo off
chcp 65001 >nul
title AI饮食健康助手 - 启动
echo.
echo ============================================
echo    AI饮食健康助手 - 快速启动
echo ============================================
echo.

echo [1/2] 正在启动后端...
start "AI Diet Backend" cmd /k "cd /d f:\ai-diet-health-assistant\backend && C:\Users\hgdcy\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [2/2] 正在启动前端...
timeout /t 2 /nobreak >nul
start "AI Diet Frontend" cmd /k "cd /d f:\ai-diet-health-assistant\frontend && npm run dev"

echo.
echo ============================================
echo    服务正在启动中...
echo    前端地址: http://localhost:5173
echo    后端地址: http://localhost:8000
echo ============================================
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.
echo 启动完成！浏览器已自动打开。
pause
