"""
食物识别服务 - 支持多种识别模式：
- mock: 模拟数据（用于测试）
- deepseek: 使用DeepSeek Vision API
- yolo: 使用本地YOLO模型（支持YOLO-World开放词汇检测）
"""

from pathlib import Path
import base64
import json
import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

_model = None


class VisionAPIError(Exception):
    pass


def predict_food_from_image(image_path: str) -> list[dict]:
    mode = getattr(settings, 'FOOD_RECOGNITION_MODE', 'mock').lower()
    logger.info(f"食物识别模式: {mode}")

    if mode == 'deepseek':
        return _vision_predict(image_path)
    elif mode == 'yolo':
        model_path = Path(settings.YOLO_MODEL_PATH)
        if model_path.exists():
            return _real_predict(image_path)
        logger.warning(f"YOLO模型文件不存在: {model_path}，回退到模拟数据")
        return _mock_predict(image_path)
    else:
        return _mock_predict(image_path)


def _get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        model_path = Path(settings.YOLO_MODEL_PATH)
        logger.info(f"加载YOLO模型: {model_path}")
        _model = YOLO(str(model_path))
        logger.info(f"模型类别: {list(_model.names.values())[:10]}... (共{len(_model.names)}类)")
    return _model


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
            else:
                logger.info(f"识别到非食物物体: {class_name} (conf: {conf:.2f})")

    return predictions


def _image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _vision_predict(image_path: str) -> list[dict]:
    api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
    if not api_key:
        raise VisionAPIError("API Key 未配置，请在 .env 中设置 DEEPSEEK_API_KEY")

    img_base64 = _image_to_base64(image_path)

    url = f"{settings.DEEPSEEK_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = """识别图片中的食物并返回JSON：[{"food_name":"食物名","confidence":0.95,"calories":200,"protein":10.5,"fat":5.2,"carbohydrates":30.0,"serving_size":"约200g"}]"""

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
        "temperature": 0.0
    }

    logger.info(f"调用Vision API: {url}, model: {settings.DEEPSEEK_MODEL}")

    try:
        with httpx.Client(trust_env=False) as client:
            response = client.post(url, json=payload, headers=headers, timeout=60)
    except httpx.TimeoutException:
        raise VisionAPIError("AI识别服务请求超时，请稍后重试")
    except httpx.ConnectError:
        raise VisionAPIError("无法连接AI识别服务，请检查网络")

    result = response.json()

    if response.status_code == 403:
        err_msg = result.get('message', '') if isinstance(result, dict) else ''
        if 'balance' in err_msg.lower() or 'insufficient' in err_msg.lower():
            raise VisionAPIError("AI识别服务余额不足，请充值后重试")
        raise VisionAPIError(f"AI识别服务拒绝访问: {err_msg}")

    if response.status_code == 401:
        raise VisionAPIError("API Key 无效，请检查 DEEPSEEK_API_KEY 配置")

    if 'error' in result:
        err_info = result['error']
        err_msg = err_info.get('message', str(err_info)) if isinstance(err_info, dict) else str(err_info)
        logger.error(f"Vision API返回错误: {err_info}")
        raise VisionAPIError(f"AI识别服务错误: {err_msg}")

    if response.status_code != 200:
        logger.error(f"Vision API HTTP错误: {response.status_code}, {result}")
        raise VisionAPIError(f"AI识别服务返回异常状态码: {response.status_code}")

    predictions = []
    if 'choices' in result and len(result['choices']) > 0:
        content = result['choices'][0]['message']['content']
        logger.info(f"Vision API返回内容: {content[:200]}")

        json_str = content.strip()

        if json_str.startswith('```'):
            parts = json_str.split('```')
            for i in range(1, len(parts), 2):
                part = parts[i].strip()
                if part.startswith('json'):
                    part = part[4:].strip()
                if part.startswith('[') or part.startswith('{'):
                    json_str = part
                    break
            else:
                part = parts[1].strip()
                if part.startswith('json'):
                    part = part[4:].strip()
                json_str = part

        start = json_str.find('[')
        end = json_str.rfind(']') + 1
        if start != -1 and end > start:
            json_str = json_str[start:end]

        try:
            foods = json.loads(json_str)
        except json.JSONDecodeError:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                foods = json.loads(content[start:end])
            else:
                logger.warning(f"无法解析Vision API返回的JSON: {content[:200]}")
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

    if predictions:
        logger.info(f"Vision API识别成功: {predictions}")
        return predictions
    else:
        logger.warning("Vision API未识别到食物")
        return []


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
