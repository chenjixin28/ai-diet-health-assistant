"""
LLM 大模型推荐服务（支持 OpenAI 兼容接口，含模拟降级）
"""

import json
from typing import AsyncGenerator, Optional

import httpx

from app.config import settings
from app.models.user import HealthGoal
from app.services.nutrition_calculator import get_nutrition_by_name


async def recommend_meal_stream(
    health_goal: Optional[str],
    target_calories: int,
    preferences: str = "",
) -> AsyncGenerator[str, None]:
    if settings.LLM_API_KEY and settings.LLM_API_KEY != "your_llm_api_key":
        async for chunk in _real_stream(health_goal, target_calories, preferences):
            yield chunk
    else:
        async for chunk in _mock_stream(health_goal, target_calories):
            yield chunk


async def _real_stream(
    health_goal: Optional[str],
    target_calories: int,
    preferences: str = "",
) -> AsyncGenerator[str, None]:
    goal_map = {
        "lose_fat": "减脂",
        "build_muscle": "增肌",
        "control_sugar": "控糖",
    }
    goal_text = goal_map.get(health_goal, "均衡饮食")

    system_prompt = (
        f"你是一位资深营养师。请根据以下条件为用户设计一天的饮食计划，"
        f"用中文回复，格式简洁清晰。\n"
        f"目标：{goal_text}\n"
        f"每日目标热量：{target_calories} kcal\n"
        f"用户偏好：{preferences or '无特殊要求'}\n"
        f"输出格式：早餐、午餐、晚餐、加餐，每餐说明食物和估算热量。"
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            f"{settings.LLM_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请给我推荐今天的饮食计划"},
                ],
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        content = data["choices"][0]["delta"].get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


async def _mock_stream(
    health_goal: Optional[str],
    target_calories: int,
) -> AsyncGenerator[str, None]:
    import asyncio

    goal_templates = {
        "lose_fat": (
            f"## 🥞 早餐 · 约 380 kcal\n"
            f"全麦面包 2 片 + 水煮蛋 1 个 + 低脂牛奶 200ml + 小番茄 5 颗\n\n"
            f"## 🍱 午餐 · 约 520 kcal\n"
            f"糙米饭 150g + 清蒸鸡胸肉 120g + 西兰花 100g + 胡萝卜 50g\n\n"
            f"## 🥗 晚餐 · 约 350 kcal\n"
            f"藜麦沙拉 + 煎三文鱼 100g + 菠菜 + 橄榄油 5ml\n\n"
            f"## 🍎 加餐 · 约 150 kcal\n"
            f"希腊酸奶 100g + 蓝莓 50g + 核桃 15g\n\n"
            f"> 🎯 总热量约 1400 kcal · 高蛋白低脂 · 适合减脂期"
        ),
        "build_muscle": (
            f"## 🥞 早餐 · 约 650 kcal\n"
            f"燕麦 80g + 全脂牛奶 300ml + 鸡蛋 3 个 + 香蕉 1 根\n\n"
            f"## 🍱 午餐 · 约 750 kcal\n"
            f"白米饭 250g + 牛排 200g + 西兰花 150g + 橄榄油 10ml\n\n"
            f"## 🥗 晚餐 · 约 650 kcal\n"
            f"红薯 200g + 三文鱼 200g + 芦笋 100g + 坚果 30g\n\n"
            f"## 🍎 加餐 · 约 350 kcal\n"
            f"蛋白粉 30g + 全脂酸奶 200g + 花生酱 20g\n\n"
            f"> 🎯 总热量约 2400 kcal · 高蛋白 · 适合增肌期"
        ),
        "control_sugar": (
            f"## 🥞 早餐 · 约 350 kcal\n"
            f"燕麦片 50g + 无糖豆浆 250ml + 水煮蛋 1 个 + 黄瓜半根\n\n"
            f"## 🍱 午餐 · 约 480 kcal\n"
            f"荞麦面 150g + 清蒸鱼 120g + 凉拌苦瓜 100g\n\n"
            f"## 🥗 晚餐 · 约 400 kcal\n"
            f"豆腐 150g + 清炒时蔬 200g + 菌菇汤 + 杂粮饭 100g\n\n"
            f"## 🍎 加餐 · 约 120 kcal\n"
            f"圣女果 10 颗 + 核桃 10g\n\n"
            f"> 🎯 总热量约 1350 kcal · 低 GI · 适合控糖人群"
        ),
        "default": (
            f"## 🥞 早餐 · 约 450 kcal\n"
            f"全麦三明治 + 鸡蛋 + 生菜 + 牛奶 200ml\n\n"
            f"## 🍱 午餐 · 约 600 kcal\n"
            f"米饭 200g + 红烧鸡块 150g + 炒青菜 150g\n\n"
            f"## 🥗 晚餐 · 约 500 kcal\n"
            f"红薯 150g + 清蒸鱼 150g + 番茄蛋汤\n\n"
            f"## 🍎 加餐 · 约 200 kcal\n"
            f"苹果 1 个 + 杏仁 15g\n\n"
            f"> 🎯 总热量约 1750 kcal · 均衡营养 · 适合日常健康"
        ),
    }

    template = goal_templates.get(health_goal, goal_templates["default"])
    words = template.replace("\n", "\n ").split()
    for i, word in enumerate(words):
        yield word + " "
        await asyncio.sleep(0.03)
