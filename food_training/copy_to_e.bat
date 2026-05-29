@echo off
chcp 65001 >nul
echo ========================================
echo   Copy food_training to E: drive
echo ========================================
echo.

set SRC=f:\ai-diet-health-assistant\food_training
set DST=E:\ultralytics-main\ultralytics-main

echo Source: %SRC%
echo Target: %DST%
echo.

echo Copying food_data.yaml...
copy /Y "%SRC%\food_data.yaml" "%DST%\food_data.yaml"

echo Copying train_food.py...
copy /Y "%SRC%\train_food.py" "%DST%\train_food.py"

echo Copying food_dataset (images + labels)...
robocopy "%SRC%\food_dataset" "%DST%\food_dataset" /E /NFL /NDL /NJH /NJS

echo.
echo ========================================
echo   Done! Now run:
echo     cd E:\ultralytics-main\ultralytics-main
echo     python train_food.py
echo ========================================
pause
