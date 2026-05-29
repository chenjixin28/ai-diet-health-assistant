"""
下载 8 类简单食物图片 + 自动生成 YOLO 标签
run: python download_food_images.py
"""
import os, random, shutil
from pathlib import Path
from bing_image_downloader import downloader as bd
from PIL import Image

BASE = Path(r'f:\ai-diet-health-assistant\food_training')
CLASSES = ['apple', 'banana', 'egg white background', 'bread food',
           'orange fruit', 'tomato', 'carrot vegetable', 'milk carton']

BASE.mkdir(exist_ok=True)
(BASE / 'food_dataset' / 'images' / 'train').mkdir(parents=True, exist_ok=True)
(BASE / 'food_dataset' / 'images' / 'val').mkdir(parents=True, exist_ok=True)
(BASE / 'food_dataset' / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
(BASE / 'food_dataset' / 'labels' / 'val').mkdir(parents=True, exist_ok=True)

DOWNLOAD = BASE / 'downloads'
DOWNLOAD.mkdir(exist_ok=True)

print("=" * 50)
print("Download food images (20 per class)...")
print("=" * 50)

for cls_id, query in enumerate(CLASSES):
    cls_name = query.split()[0]
    try:
        bd.download(query, limit=20, output_dir=str(DOWNLOAD),
                    adult_filter_off=True, force_replace=False, timeout=20)
    except Exception as e:
        print(f"  {cls_name}: download failed ({e})")
        continue

    found = 0
    for subdir in DOWNLOAD.iterdir():
        if subdir.is_dir() and query.replace(" ", "_") in subdir.name:
            imgs = list(subdir.glob("*.jpg")) + list(subdir.glob("*.png")) + list(subdir.glob("*.jpeg"))
            random.shuffle(imgs)
            split = max(1, int(len(imgs) * 0.75))

            for i, img_path in enumerate(imgs):
                subset = 'train' if i < split else 'val'
                try:
                    img = Image.open(img_path).convert('RGB')
                except:
                    continue
                w, h = img.size
                new_name = f"{cls_name}_{found:04d}.jpg"
                img.save(BASE / 'food_dataset' / 'images' / subset / new_name, 'JPEG', quality=90)

                label = BASE / 'food_dataset' / 'labels' / subset / f"{cls_name}_{found:04d}.txt"
                with open(label, 'w') as f:
                    f.write(f"{cls_id} 0.5 0.5 1.0 1.0\n")
                found += 1

    print(f"  [{cls_id}] {cls_name}: {found} images")

shutil.rmtree(DOWNLOAD, ignore_errors=True)

print()
print("=" * 50)
print("Done! Check: food_training\\food_dataset\\")
print("=" * 50)
