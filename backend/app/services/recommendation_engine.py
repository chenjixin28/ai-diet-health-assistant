"""
LLM 大模型推荐服务（支持 OpenAI 兼容接口，含模拟降级）
"""

import json
from typing import AsyncGenerator, Optional

import httpx

from app.config import settings
from app.models.user import HealthGoal
from app.services.nutrition_calculator import get_nutrition_by_name


async def generate_dietary_advice(records: list, profile) -> str:
    if settings.LLM_API_KEY and settings.LLM_API_KEY != "your_llm_api_key":
        try:
            return await _real_advice(records, profile)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"LLM建议生成失败，使用本地降级: {e}")
            return _mock_advice(records, profile)
    else:
        return _mock_advice(records, profile)


async def _real_advice(records, profile) -> str:
    goal_map = {"lose_fat": "减脂", "build_muscle": "增肌", "control_sugar": "控糖"}
    goal_text = "未设置"
    target_cal = 2000
    if profile:
        if profile.health_goal:
            goal_text = goal_map.get(profile.health_goal.value, profile.health_goal.value)
        if profile.daily_calorie_target:
            target_cal = profile.daily_calorie_target

    total_cal = sum(r.calories for r in records)
    total_protein = sum(r.protein for r in records)
    total_fat = sum(r.fat for r in records)
    total_carb = sum(r.carbohydrates for r in records)

    food_list = "\n".join(
        f"- {get_meal_label(r.meal_type)}: {r.food_name} ({r.calories:.0f}kcal, 蛋白{r.protein:.0f}g)"
        for r in records
    )

    prompt = (
        f"用户今日饮食记录：\n"
        f"{food_list}\n\n"
        f"汇总：总热量 {total_cal:.0f}kcal，蛋白质 {total_protein:.0f}g，脂肪 {total_fat:.0f}g，碳水 {total_carb:.0f}g\n"
        f"用户目标：{goal_text}，目标热量 {target_cal}kcal\n\n"
        f"你是一位资深营养师。请分析以上数据：\n"
        f"1. 总热量是否合理（相比目标）\n"
        f"2. 三大营养素比例是否均衡\n"
        f"3. 给出2-3条具体的改进建议\n"
        f"用中文简洁回复，不超过300字。"
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.LLM_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "max_tokens": 600,
                "temperature": 0.7,
            },
        )
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]


def _mock_advice(records, profile) -> str:
    if not records:
        return "今日暂无饮食记录，请先在「食物识别」中拍照记下你吃了什么，再来获取膳食建议吧！"

    total_cal = sum(r.calories for r in records)
    total_protein = sum(r.protein for r in records)
    total_fat = sum(r.fat for r in records)
    total_carb = sum(r.carbohydrates for r in records)

    target_cal = 2000
    if profile and profile.daily_calorie_target:
        target_cal = profile.daily_calorie_target

    cal_ratio = total_cal / max(target_cal, 1)
    advice = f"## 📊 今日饮食分析\n\n"
    advice += f"热量摄入：{total_cal:.0f} kcal / 目标 {target_cal} kcal"
    if cal_ratio < 0.7:
        advice += "（偏低）\n\n"
        advice += f"蛋白质 {total_protein:.0f}g · 脂肪 {total_fat:.0f}g · 碳水 {total_carb:.0f}g\n\n"
        advice += "## 💡 建议\n\n"
        advice += "1. 目前热量摄入不足，建议增加一餐或加餐补充能量\n"
        advice += "2. 可选择坚果、全脂酸奶等高营养密度食物作为加餐\n"
        advice += "3. 确保每餐都有优质蛋白质来源（鸡蛋、鱼肉、豆制品）"
    elif cal_ratio > 1.3:
        advice += "（超标）\n\n"
        advice += f"蛋白质 {total_protein:.0f}g · 脂肪 {total_fat:.0f}g · 碳水 {total_carb:.0f}g\n\n"
        advice += "## 💡 建议\n\n"
        advice += "1. 热量摄入偏高，下一餐可适当减少主食和油脂\n"
        advice += "2. 多吃蔬菜增加饱腹感，减少高热量密度的加工食品\n"
        advice += "3. 尝试用蒸、煮替代煎、炸的烹饪方式"
    else:
        advice += "（合理）\n\n"
        advice += f"蛋白质 {total_protein:.0f}g · 脂肪 {total_fat:.0f}g · 碳水 {total_carb:.0f}g\n\n"
        advice += "## 💡 建议\n\n"
        advice += "1. 热量控制在合理范围，继续保持！\n"
        advice += "2. 注意三大营养素均衡，蛋白质不低于60g/天\n"
        advice += "3. 每天保证500g蔬菜摄入，补充膳食纤维"

    return advice

async def recommend_meal_stream(
    health_goal: Optional[str],
    target_calories: int,
    preferences: str = "",
    pre_text: str = "",
) -> AsyncGenerator[str, None]:
    if settings.LLM_API_KEY and settings.LLM_API_KEY != "your_llm_api_key":
        async for chunk in _real_stream(health_goal, target_calories, preferences):
            yield chunk
    elif pre_text:
        async for chunk in _simple_stream(pre_text):
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


def get_meal_label(meal_type: str) -> str:
    labels = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐", "snack": "零食"}
    return labels.get(meal_type, meal_type)


async def _simple_stream(text: str) -> AsyncGenerator[str, None]:
    import asyncio
    for char in text:
        yield char
        await asyncio.sleep(0.008)


def format_meal_plan_text(plan, target_calories: int) -> str:
    goal_map = {"lose_fat": "减脂", "build_muscle": "增肌", "control_sugar": "控糖"}
    goal_text = goal_map.get(plan.goal_type, "健康饮食")
    text = (
        f"## 🥞 早餐\n{plan.breakfast}\n\n"
        f"## 🍱 午餐\n{plan.lunch}\n\n"
        f"## 🥗 晚餐\n{plan.dinner}\n\n"
        f"## 🍎 加餐\n{plan.snack}\n\n"
    )
    if plan.total_calories:
        text += f"> 🎯 本套食谱约 {plan.total_calories} kcal"
        if target_calories:
            diff = plan.total_calories - target_calories
            sign = "+" if diff > 0 else ""
            text += f"（目标 {target_calories} kcal，{sign}{diff}）"
        text += f" · 适合{goal_text}人群"
    else:
        text += f"> 🎯 适合{goal_text}人群"

    tips = (
        "\n\n💡 烹饪方式：优先蒸、煮、白灼、清炒、少油煎，拒绝油炸糖醋。\n"
        "💡 全天饮用温水，不喝含糖饮料。\n"
        "💡 可根据饱腹感适当增减分量。"
    )
    text += tips
    return text
