"""使用 icrawler 快速下载食物图片"""
import os, random, shutil
from pathlib import Path
from icrawler.builtin import GoogleImageCrawler
from PIL import Image

BASE = Path(r'f:\ai-diet-health-assistant\food_training')
CLASSES = ['apple', 'banana', 'egg', 'bread slice', 'orange', 'tomato', 'carrot', 'milk']

(BASE / 'food_dataset' / 'images' / 'train').mkdir(parents=True, exist_ok=True)
(BASE / 'food_dataset' / 'images' / 'val').mkdir(parents=True, exist_ok=True)
(BASE / 'food_dataset' / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
(BASE / 'food_dataset' / 'labels' / 'val').mkdir(parents=True, exist_ok=True)

print("Downloading food images (15 per class)...")
print("=" * 50)

for cls_id, cls_name in enumerate(CLASSES):
    query = f"{cls_name} single food"
    dl_dir = str(BASE / 'downloads' / cls_name)
    os.makedirs(dl_dir, exist_ok=True)

    try:
        crawler = GoogleImageCrawler(storage={'root_dir': dl_dir})
        crawler.crawl(keyword=query, max_num=15)
    except Exception as e:
        print(f"  {cls_name}: crawl failed ({e})")
        continue

    imgs = list(Path(dl_dir).glob("*.*"))
    valid = []
    for p in imgs:
        try:
            img = Image.open(p).convert('RGB')
            if img.width > 50 and img.height > 50:
                valid.append(p)
        except:
            pass

    random.shuffle(valid)
    split = max(1, int(len(valid) * 0.75))

    for i, img_path in enumerate(valid):
        subset = 'train' if i < split else 'val'
        try:
            img = Image.open(img_path).convert('RGB')
        except:
            continue
        new_name = f"{cls_name}_{i:04d}.jpg"
        img.save(BASE / 'food_dataset' / 'images' / subset / new_name, 'JPEG', quality=90)
        label = BASE / 'food_dataset' / 'labels' / subset / f"{cls_name}_{i:04d}.txt"
        with open(label, 'w') as f:
            f.write(f"{cls_id} 0.5 0.5 1.0 1.0\n")

    print(f"  [{cls_id}] {cls_name}: {len(valid)} images")

shutil.rmtree(BASE / 'downloads', ignore_errors=True)
print("=" * 50)
print("Done!")
