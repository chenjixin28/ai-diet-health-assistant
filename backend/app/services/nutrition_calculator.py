from typing import Optional
from app.config import settings


FOOD_NUTRITION_DB: list[dict] = [
    {
        "keywords": ["米饭", "白米饭", "大米饭"],
        "food_name": "米饭",
        "calories": 116,
        "protein": 2.6,
        "fat": 0.3,
        "carbohydrates": 25.9,
        "serving_size": "100g",
    },
    {
        "keywords": ["红烧肉", "扣肉"],
        "food_name": "红烧肉",
        "calories": 395,
        "protein": 7.2,
        "fat": 38.0,
        "carbohydrates": 4.0,
        "serving_size": "100g",
    },
    {
        "keywords": ["青菜", "炒青菜", "油菜", "小白菜"],
        "food_name": "炒青菜",
        "calories": 35,
        "protein": 2.0,
        "fat": 2.5,
        "carbohydrates": 1.5,
        "serving_size": "100g",
    },
    {
        "keywords": ["鸡胸肉", "鸡肉", "煎鸡胸"],
        "food_name": "鸡胸肉",
        "calories": 133,
        "protein": 31.0,
        "fat": 1.2,
        "carbohydrates": 0.0,
        "serving_size": "100g",
    },
    {
        "keywords": ["三文鱼", "三文鱼刺身", "烤三文鱼"],
        "food_name": "三文鱼",
        "calories": 208,
        "protein": 20.0,
        "fat": 13.0,
        "carbohydrates": 0.0,
        "serving_size": "100g",
    },
    {
        "keywords": ["西兰花", "花菜", "西兰花炒"],
        "food_name": "西兰花",
        "calories": 34,
        "protein": 2.8,
        "fat": 0.4,
        "carbohydrates": 6.6,
        "serving_size": "100g",
    },
    {
        "keywords": ["面条", "拉面", "汤面", "炒面"],
        "food_name": "面条",
        "calories": 280,
        "protein": 8.5,
        "fat": 1.5,
        "carbohydrates": 57.0,
        "serving_size": "100g(熟)",
    },
    {
        "keywords": ["鸡蛋", "水煮蛋", "煎蛋", "炒蛋"],
        "food_name": "鸡蛋",
        "calories": 144,
        "protein": 13.3,
        "fat": 9.5,
        "carbohydrates": 1.5,
        "serving_size": "2个(100g)",
    },
    {
        "keywords": ["牛奶", "纯牛奶", "低脂牛奶"],
        "food_name": "牛奶",
        "calories": 54,
        "protein": 3.0,
        "fat": 3.2,
        "carbohydrates": 3.4,
        "serving_size": "100ml",
    },
    {
        "keywords": ["面包", "全麦面包", "吐司"],
        "food_name": "全麦面包",
        "calories": 246,
        "protein": 9.0,
        "fat": 3.5,
        "carbohydrates": 43.0,
        "serving_size": "2片(80g)",
    },
    {
        "keywords": ["苹果"],
        "food_name": "苹果",
        "calories": 52,
        "protein": 0.3,
        "fat": 0.2,
        "carbohydrates": 13.5,
        "serving_size": "1个(200g)",
    },
    {
        "keywords": ["香蕉"],
        "food_name": "香蕉",
        "calories": 89,
        "protein": 1.1,
        "fat": 0.3,
        "carbohydrates": 22.8,
        "serving_size": "1根(120g)",
    },
    {
        "keywords": ["饺子", "水饺"],
        "food_name": "饺子",
        "calories": 240,
        "protein": 10.0,
        "fat": 8.0,
        "carbohydrates": 30.0,
        "serving_size": "10个(200g)",
    },
    {
        "keywords": ["披萨", "比萨"],
        "food_name": "披萨",
        "calories": 266,
        "protein": 11.0,
        "fat": 10.0,
        "carbohydrates": 33.0,
        "serving_size": "1片(100g)",
    },
    {
        "keywords": ["汉堡", "汉堡包"],
        "food_name": "汉堡",
        "calories": 295,
        "protein": 17.0,
        "fat": 12.0,
        "carbohydrates": 30.0,
        "serving_size": "1个(150g)",
    },
    {
        "keywords": ["沙拉", "蔬菜沙拉", "藜麦沙拉"],
        "food_name": "沙拉",
        "calories": 120,
        "protein": 5.0,
        "fat": 6.0,
        "carbohydrates": 12.0,
        "serving_size": "1份(200g)",
    },
    {
        "keywords": ["牛肉", "牛排", "煎牛排"],
        "food_name": "牛排",
        "calories": 250,
        "protein": 26.0,
        "fat": 15.0,
        "carbohydrates": 0.0,
        "serving_size": "100g",
    },
    {
        "keywords": ["豆腐", "麻婆豆腐"],
        "food_name": "豆腐",
        "calories": 76,
        "protein": 8.1,
        "fat": 3.7,
        "carbohydrates": 2.8,
        "serving_size": "100g",
    },
    {
        "keywords": ["寿司", "三文鱼寿司"],
        "food_name": "寿司",
        "calories": 145,
        "protein": 7.0,
        "fat": 1.0,
        "carbohydrates": 27.0,
        "serving_size": "6个(150g)",
    },
    {
        "keywords": ["咖啡", "拿铁", "美式"],
        "food_name": "咖啡",
        "calories": 2,
        "protein": 0.1,
        "fat": 0.0,
        "carbohydrates": 0.3,
        "serving_size": "1杯(240ml)",
    },
]


def recognize_food(food_description: str) -> Optional[dict]:
    desc_lower = food_description.lower()
    best_match = None
    best_score = 0

    for item in FOOD_NUTRITION_DB:
        for kw in item["keywords"]:
            kw_lower = kw.lower()
            if kw_lower in desc_lower:
                score = len(kw_lower)
                if score > best_score:
                    best_score = score
                    best_match = item

    return best_match


def search_food_by_name(name: str) -> list[dict]:
    name_lower = name.lower()
    results = []
    for item in FOOD_NUTRITION_DB:
        for kw in item["keywords"]:
            if name_lower in kw.lower():
                results.append(item)
                break
    return results if results else FOOD_NUTRITION_DB[:5]


def get_nutrition_by_name(food_name: str) -> Optional[dict]:
    for item in FOOD_NUTRITION_DB:
        if item["food_name"] == food_name:
            return item
    return recognize_food(food_name)
