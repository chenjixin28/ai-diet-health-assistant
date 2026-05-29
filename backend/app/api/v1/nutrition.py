from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.food_record import FoodRecord
from app.schemas.user import ApiResponse
from app.services.recommendation_engine import recommend_meal_stream
from app.api.deps import get_current_user

router = APIRouter(prefix="/nutrition", tags=["营养分析"])


@router.get("/summary", response_model=ApiResponse)
def get_nutrition_summary(
    days: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timedelta

    today = datetime.utcnow().replace(hour=23, minute=59, second=59)
    start_date = today - timedelta(days=days - 1)

    records = (
        db.query(FoodRecord)
        .filter(
            FoodRecord.user_id == current_user.id,
            FoodRecord.recorded_at >= start_date,
        )
        .all()
    )

    daily: dict[str, dict] = {}
    for r in records:
        date_key = r.recorded_at.strftime("%Y-%m-%d")
        if date_key not in daily:
            daily[date_key] = {
                "date": date_key,
                "total_calories": 0,
                "total_protein": 0,
                "total_fat": 0,
                "total_carbohydrates": 0,
                "meal_count": 0,
            }
        daily[date_key]["total_calories"] += r.calories
        daily[date_key]["total_protein"] += r.protein
        daily[date_key]["total_fat"] += r.fat
        daily[date_key]["total_carbohydrates"] += r.carbohydrates
        daily[date_key]["meal_count"] += 1

    result = sorted(daily.values(), key=lambda x: x["date"])

    return ApiResponse(
        success=True,
        detail="营养摘要查询成功",
        data={"summary": result},
    )


@router.get("/today", response_model=ApiResponse)
def get_today_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime
    from sqlalchemy import func as sa_func

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)

    stats = (
        db.query(
            sa_func.count(FoodRecord.id),
            sa_func.sum(FoodRecord.calories),
            sa_func.sum(FoodRecord.protein),
            sa_func.sum(FoodRecord.fat),
            sa_func.sum(FoodRecord.carbohydrates),
        )
        .filter(
            FoodRecord.user_id == current_user.id,
            FoodRecord.recorded_at >= today_start,
            FoodRecord.recorded_at <= today_end,
        )
        .first()
    )

    return ApiResponse(
        success=True,
        detail="今日摘要",
        data={
            "meal_count": int(stats[0] or 0),
            "total_calories": float(stats[1] or 0),
            "total_protein": float(stats[2] or 0),
            "total_fat": float(stats[3] or 0),
            "total_carbohydrates": float(stats[4] or 0),
        },
    )


@router.get("/recommend", response_model=None)
async def recommend_meal(
    health_goal: str = Query(default="lose_fat"),
    target_calories: int = Query(default=2000, ge=500, le=5000),
    preferences: str = Query(default=""),
    current_user: User = Depends(get_current_user),
):
    profile = current_user.health_profile
    goal = health_goal
    calories = target_calories

    if profile:
        if profile.health_goal:
            goal = profile.health_goal.value
        if profile.daily_calorie_target:
            calories = profile.daily_calorie_target

    return StreamingResponse(
        recommend_meal_stream(health_goal=goal, target_calories=calories, preferences=preferences),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
