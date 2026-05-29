from ultralytics import YOLO
import os

os.chdir(r'E:\ultralytics-main\ultralytics-main')

model = YOLO('yolo11n.pt')

model.train(
    data='food_data.yaml',
    epochs=50,
    device='cpu',
    amp=False,
    batch=1,
    imgsz=416,
    patience=20,
    name='food_train',
)
