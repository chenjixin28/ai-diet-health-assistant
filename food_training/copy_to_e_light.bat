@echo off
echo ================================================
echo   复制轻量训练文件到 E 盘
echo ================================================
echo.

set SOURCE=f:\ai-diet-health-assistant\food_training
set DEST=E:\ultralytics-main\ultralytics-main

echo 正在复制文件...
echo.

xcopy "%SOURCE%\food_data_simple.yaml" "%DEST%\" /Y
xcopy "%SOURCE%\train_food_light.py" "%DEST%\" /Y
xcopy /E /I "%SOURCE%\food_dataset" "%DEST%\food_dataset"

echo.
echo ================================================
echo   复制完成！
echo ================================================
echo.
echo 训练步骤：
echo 1. 打开命令提示符
echo 2. cd /d E:\ultralytics-main\ultralytics-main
echo 3. python train_food_light.py
echo.
pause
