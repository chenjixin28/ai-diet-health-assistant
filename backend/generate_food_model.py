#!/usr/bin/env python3
"""
生成 YOLO-World 食物专用模型
通过 set_classes 设置食物类别，保存为独立 .pt 文件
"""

from ultralytics import YOLO

FOOD_CLASSES = [
    "rice",
    "noodles",
    "bread",
    "sandwich",
    "hamburger",
    "pizza",
    "hot dog",
    "donut",
    "cake",
    "egg",
    "chicken",
    "beef",
    "steak",
    "pork",
    "fish",
    "salmon",
    "shrimp",
    "tofu",
    "salad",
    "soup",
    "dumpling",
    "sushi",
    "apple",
    "banana",
    "orange",
    "broccoli",
    "carrot",
    "tomato",
    "potato",
    "cucumber",
    "milk",
    "coffee",
    "tea",
    "juice",
    "bottle",
    "bowl",
    "plate",
    "cup",
]

def main():
    print("Loading yolov8s-worldv2.pt ...")
    model = YOLO("yolov8s-worldv2.pt")

    print(f"Setting {len(FOOD_CLASSES)} food classes...")
    model.set_classes(FOOD_CLASSES)

    output_path = "models/yolov8_food_world.pt"
    model.save(output_path)
    print(f"Saved to {output_path}")

    print("\nFood classes in model:")
    for i, name in enumerate(FOOD_CLASSES):
        print(f"  {i}: {name}")

    print("\nDone!")

if __name__ == "__main__":
    main()
