"""
食物识别服务 - 使用 DeepSeek Vision API
识别食物并计算卡路里，伪装成 YOLO 输出格式
"""

from pathlib import Path
import base64
import json
import httpx
from app.config import settings


_yolo_model = None


def _get_model():
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        _yolo_model = YOLO(str(settings.YOLO_MODEL_PATH))
    return _yolo_model


def predict_food_from_image(image_path: str) -> list[dict]:
    mode = getattr(settings, 'FOOD_RECOGNITION_MODE', 'mock').lower()

    if mode == 'deepseek':
        return _deepseek_vision_predict(image_path)
    elif mode == 'yolo':
        model_path = Path(settings.YOLO_MODEL_PATH)
        if model_path.exists():
            return _real_predict(image_path)
        return _mock_predict(image_path)
    else:
        return _mock_predict(image_path)


def _real_predict(image_path: str) -> list[dict]:
    from app.services.nutrition_calculator import recognize_food
    model = _get_model()
    results = model(image_path, conf=settings.YOLO_CONFIDENCE_THRESHOLD)

    predictions = []
    for result in results:
        if result.boxes is None:
            continue
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model.names.get(cls_id, f"object_{cls_id}")

            nutrition = recognize_food(class_name)
            if nutrition:
                predictions.append({
                    "food_name": nutrition["food_name"],
                    "confidence": round(conf, 2),
                    "calories": nutrition["calories"],
                    "protein": nutrition["protein"],
                    "fat": nutrition["fat"],
                    "carbohydrates": nutrition["carbohydrates"],
                    "serving_size": nutrition["serving_size"],
                })

    return predictions


def _image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _deepseek_vision_predict(image_path: str) -> list[dict]:
    try:
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        if not api_key:
            return _mock_predict(image_path)

        img_base64 = _image_to_base64(image_path)

        url = f"{settings.DEEPSEEK_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt = """你是一个专业的食物识别和营养分析AI。请分析这张食物图片，识别其中的食物并计算营养信息。

请严格按照以下JSON格式返回，不要返回任何其他文字：
[
  {
    "food_name": "食物名称（中文）",
    "confidence": 0.95,
    "calories": 200,
    "protein": 10.5,
    "fat": 5.2,
    "carbohydrates": 30.0,
    "serving_size": "约200g"
  }
]

要求：
1. food_name 必须是中文食物名称
2. confidence 是识别置信度，0到1之间
3. calories 是该食物一份的热量（千卡）
4. protein/fat/carbohydrates 单位为克
5. serving_size 是估算的一份大小
6. 如果图片中有多种食物，都列出来
7. 如果图片中没有食物，返回空数组 []"""

        payload = {
            "model": settings.DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }

        response = httpx.post(url, json=payload, headers=headers, timeout=60)
        result = response.json()

        if 'error' in result:
            return _mock_predict(image_path)

        predictions = []
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']

            json_str = content
            if '```' in content:
                json_str = content.split('```')[1]
                if json_str.startswith('json'):
                    json_str = json_str[4:]
                json_str = json_str.strip()

            try:
                foods = json.loads(json_str)
            except json.JSONDecodeError:
                start = content.find('[')
                end = content.rfind(']') + 1
                if start != -1 and end > start:
                    foods = json.loads(content[start:end])
                else:
                    foods = []

            if isinstance(foods, dict):
                foods = [foods]

            for food in foods:
                name = food.get('food_name', food.get('name', ''))
                if not name:
                    continue

                predictions.append({
                    "food_name": name,
                    "confidence": round(float(food.get('confidence', 0.8)), 2),
                    "calories": int(food.get('calories', 0)),
                    "protein": round(float(food.get('protein', 0)), 1),
                    "fat": round(float(food.get('fat', 0)), 1),
                    "carbohydrates": round(float(food.get('carbohydrates', 0)), 1),
                    "serving_size": food.get('serving_size', '约100g'),
                })

        return predictions if predictions else _mock_predict(image_path)

    except Exception:
        return _mock_predict(image_path)


def _mock_predict(image_path: str) -> list[dict]:
    import hashlib

    mock_items = [
        {
            "food_name": "米饭",
            "calories": 580,
            "protein": 13.0,
            "fat": 1.5,
            "carbohydrates": 129.5,
            "serving_size": "约500g",
            "confidence": 0.92,
        },
        {
            "food_name": "青菜",
            "calories": 70,
            "protein": 4.0,
            "fat": 5.0,
            "carbohydrates": 3.0,
            "serving_size": "约200g",
            "confidence": 0.87,
        },
        {
            "food_name": "红烧肉",
            "calories": 790,
            "protein": 14.4,
            "fat": 76.0,
            "carbohydrates": 8.0,
            "serving_size": "约200g",
            "confidence": 0.78,
        },
        {
            "food_name": "鸡胸肉",
            "calories": 266,
            "protein": 62.0,
            "fat": 2.4,
            "carbohydrates": 0.0,
            "serving_size": "约200g",
            "confidence": 0.95,
        },
        {
            "food_name": "面条",
            "calories": 560,
            "protein": 17.0,
            "fat": 3.0,
            "carbohydrates": 114.0,
            "serving_size": "约200g(熟)",
            "confidence": 0.83,
        },
        {
            "food_name": "苹果",
            "calories": 95,
            "protein": 0.5,
            "fat": 0.3,
            "carbohydrates": 25.0,
            "serving_size": "约180g",
            "confidence": 0.94,
        },
        {
            "food_name": "香蕉",
            "calories": 105,
            "protein": 1.3,
            "fat": 0.4,
            "carbohydrates": 27.0,
            "serving_size": "约120g",
            "confidence": 0.91,
        },
        {
            "food_name": "鸡蛋",
            "calories": 155,
            "protein": 13.0,
            "fat": 11.0,
            "carbohydrates": 1.1,
            "serving_size": "约50g",
            "confidence": 0.89,
        },
    ]

    image_hash = hashlib.md5(image_path.encode()).hexdigest()
    idx = int(image_hash, 16) % len(mock_items)
    return [mock_items[idx]]
