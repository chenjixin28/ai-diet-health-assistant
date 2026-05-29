import os

base = r'E:\ultralytics-main\ultralytics-main'

yaml_content = """path: ./food_dataset
train: images/train
val: images/val

nc: 8
names:
  0: apple
  1: banana
  2: egg
  3: bread
  4: orange
  5: tomato
  6: carrot
  7: milk
"""

with open(os.path.join(base, 'food_data.yaml'), 'w', encoding='utf-8') as f:
    f.write(yaml_content)

train_script = """from ultralytics import YOLO
import os
os.chdir(r'E:\\ultralytics-main\\ultralytics-main')

model = YOLO('yolo11n.pt')

model.train(
    data='food_data.yaml',
    epochs=50,
    device='cpu',
    amp=False,
    batch=2,
    imgsz=640,
    patience=20,
    name='food_train',
)
"""

with open(os.path.join(base, 'train_food.py'), 'w', encoding='utf-8') as f:
    f.write(train_script)

print('Done: food_data.yaml + train_food.py created on E:')
