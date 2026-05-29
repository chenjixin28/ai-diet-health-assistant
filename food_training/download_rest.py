"""快速补下载剩余食物图片"""
import os, random
from pathlib import Path
from bing_image_downloader import downloader
from PIL import Image

BASE = Path(r'f:\ai-diet-health-assistant\food_training')

queries = [
    (1, 'single banana fruit white background'),
    (2, 'boiled egg single white background'),
    (3, 'slice of bread single white background'),
    (4, 'orange fruit single white background'),
    (5, 'tomato single white background'),
    (6, 'carrot single white background'),
    (7, 'glass of milk white background'),
]

for cls_id, query in queries:
    cls_name = query.split()[0]
    dl_dir = BASE / 'downloads'
    dl_dir.mkdir(exist_ok=True)
    
    print(f"Downloading {cls_name}...")
    try:
        downloader.download(query, limit=15, output_dir=str(dl_dir),
                          adult_filter_off=True, force_replace=False, timeout=30)
    except Exception as e:
        print(f"  Skip: {e}")
        continue

    found = 0
    for subdir in Path(dl_dir).iterdir():
        if subdir.is_dir():
            imgs = list(subdir.glob("*.jpg")) + list(subdir.glob("*.png")) + list(subdir.glob("*.jpeg"))
            random.shuffle(imgs)
            split = max(1, int(len(imgs) * 0.75))
            for i, img_path in enumerate(imgs):
                subset = 'train' if i < split else 'val'
                try:
                    img = Image.open(img_path).convert('RGB')
                except:
                    continue
                new_name = f"{cls_name}_{found:04d}.jpg"
                img.save(BASE / 'food_dataset' / 'images' / subset / new_name, 'JPEG', quality=90)
                label = BASE / 'food_dataset' / 'labels' / subset / f"{cls_name}_{found:04d}.txt"
                with open(label, 'w') as f:
                    f.write(f"{cls_id} 0.5 0.5 1.0 1.0\n")
                found += 1

    print(f"  [{cls_id}] {cls_name}: {found} images")
    import shutil
    shutil.rmtree(dl_dir, ignore_errors=True)

print("Done!")
