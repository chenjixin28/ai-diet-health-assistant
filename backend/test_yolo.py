#!/usr/bin/env python3
"""
测试 YOLO 本地模型推理
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.food_recognition import predict_food_from_image
from app.services.nutrition_calculator import recognize_food


def test_yolo_model():
    """测试 YOLO 模型加载和推理"""
    print("=" * 60)
    print("测试 YOLO 本地模型")
    print("=" * 60)
    
    # 打印配置
    print(f"\n配置信息:")
    print(f"  识别模式: {settings.FOOD_RECOGNITION_MODE}")
    print(f"  模型路径: {settings.YOLO_MODEL_PATH}")
    print(f"  置信度阈值: {settings.YOLO_CONFIDENCE_THRESHOLD}")
    
    # 检查模型文件
    model_path = Path(settings.YOLO_MODEL_PATH)
    if not model_path.exists():
        print(f"\n❌ 错误: 模型文件不存在: {model_path}")
        return False
    
    print(f"\n✅ 模型文件存在: {model_path} ({model_path.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # 尝试加载模型
    try:
        from app.services.food_recognition import _get_model
        print(f"\n正在加载模型...")
        model = _get_model()
        print(f"✅ 模型加载成功!")
        print(f"  可识别类别数: {len(model.names)}")
        print(f"  部分类别示例: {list(model.names.values())[:10]}")
    except Exception as e:
        print(f"\n❌ 模型加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试食物匹配
    print(f"\n测试食物类别匹配:")
    test_classes = ["apple", "banana", "orange", "broccoli", "carrot", 
                   "pizza", "donut", "cake", "hot dog", "chicken", "egg"]
    
    for cls_name in test_classes:
        match = recognize_food(cls_name)
        if match:
            print(f"  ✅ {cls_name:15} -> {match['food_name']}")
        else:
            print(f"  ⚠️  {cls_name:15} -> (未匹配)")
    
    # 如果有测试图片，尝试推理
    test_image = Path(__file__).parent / "uploads" / "test.jpg"
    if test_image.exists():
        print(f"\n测试图片推理: {test_image}")
        try:
            results = predict_food_from_image(str(test_image))
            if results:
                print(f"✅ 识别到 {len(results)} 个食物:")
                for r in results:
                    print(f"  - {r['food_name']} (conf: {r['confidence']:.2f}, {r['calories']} kcal)")
            else:
                print("⚠️  未识别到食物")
        except Exception as e:
            print(f"❌ 推理失败: {e}")
    else:
        print(f"\n⚠️  测试图片不存在: {test_image}")
        print("   请上传一张图片到 uploads/ 目录进行测试")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_yolo_model()
    sys.exit(0 if success else 1)
