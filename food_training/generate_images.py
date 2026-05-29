"""
生成简单食物占位图片（彩色形状），方便测试训练流程。
替换为真实照片后效果才好。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

BASE = Path(r'f:\ai-diet-health-assistant\food_training')
COLORS = {
    'apple':   ('#e74c3c', '#c0392b'),
    'banana':  ('#f1c40f', '#d4ac0d'),
    'egg':     ('#fdebd0', '#f5b041'),
    'bread':   ('#d4a574', '#b87333'),
    'orange':  ('#f39c12', '#e67e22'),
    'tomato':  ('#ff4444', '#cc0000'),
    'carrot':  ('#ff7f50', '#e65c00'),
    'milk':    ('#ebf5fb', '#aed6f1'),
}

TEXTS = {
    'apple': '🍎', 'banana': '🍌', 'egg': '🥚', 'bread': '🍞',
    'orange': '🍊', 'tomato': '🍅', 'carrot': '🥕', 'milk': '🥛',
}

# make sure structure exists
for subset in ['train', 'val']:
    (BASE / 'food_dataset' / 'images' / subset).mkdir(parents=True, exist_ok=True)
    (BASE / 'food_dataset' / 'labels' / subset).mkdir(parents=True, exist_ok=True)

# clear old generated images (keep apple downloads)
for cls_name in ['banana', 'egg', 'bread', 'orange', 'tomato', 'carrot', 'milk']:
    for p in (BASE / 'food_dataset' / 'images' / 'train').glob(f'{cls_name}_*.jpg'):
        p.unlink()
    for p in (BASE / 'food_dataset' / 'images' / 'val').glob(f'{cls_name}_*.jpg'):
        p.unlink()
    for p in (BASE / 'food_dataset' / 'labels' / 'train').glob(f'{cls_name}_*.txt'):
        p.unlink()
    for p in (BASE / 'food_dataset' / 'labels' / 'val').glob(f'{cls_name}_*.txt'):
        p.unlink()

for cls_id, cls_name in enumerate(COLORS):
    bg_color, fg_color = COLORS[cls_name]
    emoji = TEXTS.get(cls_name, '🍽')

    for i in range(16):
        subset = 'val' if i >= 12 else 'train'

        img = Image.new('RGB', (640, 640), 'white')
        draw = ImageDraw.Draw(img)

        # draw food "shape"
        shape_rx = random.choice(['circle', 'oval'])
        cx, cy = 320, 300
        rw = random.randint(140, 220)
        rh = random.randint(140, 220) if shape_rx == 'oval' else rw

        draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=bg_color, outline=fg_color, width=6)

        # tiny variation
        for _ in range(random.randint(0, 3)):
            sx = random.randint(cx - rw, cx + rw)
            sy = random.randint(cy - rh, cy + rh)
            sr = random.randint(20, 50)
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                         fill=random.choice(['#ffffff44', '#00000022']), outline=None)

        # emoji text
        try:
            font = ImageFont.truetype('C:\\Windows\\Fonts\\seguiemj.ttf', 80)
        except:
            font = ImageFont.load_default()
        draw.text((270, 400), emoji, fill='black', font=font, anchor='mm')

        new_name = f"{cls_name}_{i:04d}.jpg"
        img.save(BASE / 'food_dataset' / 'images' / subset / new_name, 'JPEG', quality=85)

        label = BASE / 'food_dataset' / 'labels' / subset / f"{cls_name}_{i:04d}.txt"
        with open(label, 'w') as f:
            f.write(f"{cls_id} 0.5 0.5 1.0 1.0\n")

    print(f"  [{cls_id}] {cls_name}: 16 images generated")

# Also prefix apple images correctly
apple_count = 0
for p in list((BASE / 'food_dataset' / 'images' / 'train').glob('apple_*.jpg')) + \
            list((BASE / 'food_dataset' / 'images' / 'val').glob('apple_*.jpg')):
    apple_count += 1
print(f"  [0] apple: {apple_count} images (existing)")

total = len(list((BASE / 'food_dataset' / 'images' / 'train').iterdir())) + \
        len(list((BASE / 'food_dataset' / 'images' / 'val').iterdir()))
total_labels = len(list((BASE / 'food_dataset' / 'labels' / 'train').iterdir())) + \
               len(list((BASE / 'food_dataset' / 'labels' / 'val').iterdir()))
print(f"\nTotal: {total} images, {total_labels} labels")
print("STRUCTURE COMPLETE - You can now copy to E: and train!")
