"""
筛选数据集，只保留apple和banana两个类别
用于超轻量训练测试
"""

from pathlib import Path
import shutil

BASE = Path(r'f:\ai-diet-health-assistant\food_training')
KEEP_CLASSES = ['apple', 'banana']

for subset in ['train', 'val']:
    images_dir = BASE / 'food_dataset' / 'images' / subset
    labels_dir = BASE / 'food_dataset' / 'labels' / subset

    for img_file in images_dir.glob('*.jpg'):
        cls_name = img_file.stem.rsplit('_', 1)[0]

        if cls_name not in KEEP_CLASSES:
            img_file.unlink()
            label_file = labels_dir / f"{img_file.stem}.txt"
            if label_file.exists():
                label_file.unlink()

print("数据集筛选完成！只保留 apple 和 banana 两个类别")
print("建议：替换为真实照片后再训练")
