"""
超轻量级食物识别模型训练脚本
针对CPU和低配置电脑优化
"""

from ultralytics import YOLO
import os

os.chdir(r'E:\ultralytics-main\ultralytics-main')

model = YOLO('yolov8n.pt')

model.train(
    data='food_data_simple.yaml',
    epochs=20,
    device='cpu',
    amp=False,
    batch=1,
    imgsz=320,
    patience=10,
    name='food_train_light',
    augment=False,
    hsv_h=0,
    hsv_s=0,
    hsv_v=0,
    degrees=0,
    translate=0,
    scale=0,
    flipud=0,
    fliplr=0,
    mosaic=0,
    copy_paste=0,
)
