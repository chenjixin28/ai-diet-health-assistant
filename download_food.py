"""
下载 8 类简单食物图片 + 自动生成 YOLO 标签（整图标注）
"""
import os
import random
from pathlib import Path

from bing_image_downloader import downloader as bd
from PIL import Image

BASE = Path(r'E:\ultralytics-main\ultralytics-main\food_dataset')
CLASSES = ['apple', 'banana', 'egg', 'bread', 'orange', 'tomato', 'carrot', 'milk']

(BASE / 'images' / 'train').mkdir(parents=True, exist_ok=True)
(BASE / 'images' / 'val').mkdir(parents=True, exist_ok=True)
(BASE / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
(BASE / 'labels' / 'val').mkdir(parents=True, exist_ok=True)

print("=" * 50)
print("下载食物图片（每类 30 张）...")
print("=" * 50)

all_images = {}  # class_id -> [path, ...]

for cls_id, cls_name in enumerate(CLASSES):
    query = f"{cls_name} food single white background"
    out_dir = str(BASE / 'downloads')
    try:
        bd.download(query, limit=30, output_dir=out_dir, adult_filter_off=True, force_replace=False, timeout=15)
    except Exception as e:
        print(f"  {cls_name}: 下载失败 ({e})")
        continue

    search_dir = Path(out_dir) / query.replace(" ", "_")
    images = list(search_dir.glob("*.jpg")) + list(search_dir.glob("*.png")) + list(search_dir.glob("*.jpeg"))
    all_images[cls_id] = images
    print(f"  [{cls_id}] {cls_name}: {len(images)} 张")

print()
print("=" * 50)
print("生成 YOLO 标签 + 划分训练/验证集 ...")
print("=" * 50)

for cls_id, cls_name in enumerate(CLASSES):
    images = all_images.get(cls_id, [])
    if not images:
        continue

    random.shuffle(images)
    split_idx = max(1, int(len(images) * 0.8))
    train_imgs = images[:split_idx]
    val_imgs = images[split_idx:]

    for subset, img_list in [('train', train_imgs), ('val', val_imgs)]:
        for img_path in img_list:
            try:
                img = Image.open(img_path).convert('RGB')
            except Exception:
                continue

            w, h = img.size
            new_name = f"{cls_name}_{img_path.stem}.jpg"
            dest_img = BASE / 'images' / subset / new_name
            img.save(dest_img, 'JPEG', quality=90)

            label_path = BASE / 'labels' / subset / f"{cls_name}_{img_path.stem}.txt"
            x_center = 0.5
            y_center = 0.5
            bw = 1.0
            bh = 1.0
            with open(label_path, 'w') as f:
                f.write(f"{cls_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n")

    print(f"  {cls_name}: 训练 {len(train_imgs)} 张, 验证 {len(val_imgs)} 张")

print()
print("=" * 50)
print("数据集准备完成！")
print(f"  图片: {BASE / 'images'}")
print(f"  标签: {BASE / 'labels'}")
print()
print("下一步运行: python train_food.py")
print("=" * 50)
