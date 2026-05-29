@echo off
echo ============================================
echo    AI饮食健康助手 - U盘备份脚本
echo ============================================
echo.

set "SRC_DIR=f:\ai-diet-health-assistant"

:: 检查 U 盘
for %%d in (D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\" (
        set "USB_DRIVE=%%d:"
        echo 检测到 U 盘: %%d:
        goto :found_usb
    )
)

echo 未检测到 U 盘！
pause
exit /b 1

:found_usb
echo.
echo 正在优化复制（跳过临时文件）...
echo.

set "DEST_DIR=%USB_DRIVE%\ai-diet-health-assistant"

:: 使用 Robocopy 复制，跳过不需要的文件
robocopy "%SRC_DIR%" "%DEST_DIR%" /E /XD node_modules __pycache__ venv env build dist .git .vscode .idea /XF *.log .env *.db *.sqlite *.pyc

echo.
echo ============================================
echo    复制完成！
echo    项目位置: %DEST_DIR%
echo ============================================
echo.
echo 提示: 
echo   - 如果你有自己的 .env 配置文件，请手动复制
echo   - node_modules 和 __pycache__ 已跳过（到新电脑后重新安装）
echo.
pause
