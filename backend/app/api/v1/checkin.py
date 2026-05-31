from datetime import datetime, timedelta, date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.database import get_db
from app.models.user import User
from app.models.food_record import FoodRecord
from app.schemas.user import ApiResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/checkin", tags=["打卡成就"])

ACHIEVEMENTS = [
    {
        "id": "first_checkin",
        "name": "初次打卡",
        "description": "完成第一次饮食记录",
        "icon": "🎉",
        "condition": "records >= 1",
    },
    {
        "id": "streak_3",
        "name": "三天坚持",
        "description": "连续打卡 3 天",
        "icon": "🔥",
        "condition": "streak >= 3",
    },
    {
        "id": "streak_7",
        "name": "一周达人",
        "description": "连续打卡 7 天",
        "icon": "⭐",
        "condition": "streak >= 7",
    },
    {
        "id": "streak_14",
        "name": "半月勋章",
        "description": "连续打卡 14 天",
        "icon": "🏅",
        "condition": "streak >= 14",
    },
    {
        "id": "streak_30",
        "name": "月度之王",
        "description": "连续打卡 30 天",
        "icon": "👑",
        "condition": "streak >= 30",
    },
    {
        "id": "total_10",
        "name": "小小起步",
        "description": "累计完成 10 次记录",
        "icon": "🌱",
        "condition": "total_records >= 10",
    },
    {
        "id": "total_50",
        "name": "饮食达人",
        "description": "累计完成 50 次记录",
        "icon": "🌟",
        "condition": "total_records >= 50",
    },
    {
        "id": "total_100",
        "name": "百餐记录",
        "description": "累计完成 100 次记录",
        "icon": "💎",
        "condition": "total_records >= 100",
    },
    {
        "id": "variety_5",
        "name": "五味俱全",
        "description": "记录过 5 种不同食物",
        "icon": "🍱",
        "condition": "food_variety >= 5",
    },
    {
        "id": "variety_10",
        "name": "美食探索家",
        "description": "记录过 10 种不同食物",
        "icon": "🌍",
        "condition": "food_variety >= 10",
    },
    {
        "id": "variety_20",
        "name": "百味人生",
        "description": "记录过 20 种不同食物",
        "icon": "🎖️",
        "condition": "food_variety >= 20",
    },
    {
        "id": "profile_complete",
        "name": "健康守护者",
        "description": "完善个人健康档案",
        "icon": "🛡️",
        "condition": "profile_complete",
    },
]


@router.get("/calendar", response_model=ApiResponse)
def get_calendar(
    year: int = Query(default=None),
    month: int = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    records = (
        db.query(func.date(FoodRecord.recorded_at))
        .filter(
            FoodRecord.user_id == current_user.id,
            FoodRecord.recorded_at >= month_start,
            FoodRecord.recorded_at <= month_end,
        )
        .distinct()
        .all()
    )
    checked_days = {str(r[0]) for r in records if r[0] is not None}

    calendar_days = []
    total_checkins = 0
    for d in range(1, month_end.day + 1):
        day_date = date(year, month, d)
        day_str = day_date.strftime("%Y-%m-%d")
        is_checked = day_str in checked_days
        is_today = day_date == today
        is_future = day_date > today
        if is_checked:
            total_checkins += 1
        calendar_days.append({
            "date": day_str,
            "day": d,
            "weekday": day_date.weekday(),
            "checked": is_checked,
            "is_today": is_today,
            "is_future": is_future,
        })

    all_checked = (
        db.query(func.date(FoodRecord.recorded_at))
        .filter(FoodRecord.user_id == current_user.id)
        .distinct()
        .order_by(func.date(FoodRecord.recorded_at).desc())
        .all()
    )
    all_dates = [str(r[0]) for r in all_checked if r[0] is not None]

    current_streak = 0
    check_date = today
    while True:
        if check_date.strftime("%Y-%m-%d") in all_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            if check_date == today and today.strftime("%Y-%m-%d") not in all_dates:
                pass
            else:
                break
            break

    longest_streak = 0
    temp_streak = 0
    sorted_dates = sorted(set(all_dates))
    for i, d_str in enumerate(sorted_dates):
        if i == 0:
            temp_streak = 1
        else:
            prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d").date()
            curr = datetime.strptime(d_str, "%Y-%m-%d").date()
            if (curr - prev).days == 1:
                temp_streak += 1
            else:
                temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak

    total_records = db.query(FoodRecord).filter(
        FoodRecord.user_id == current_user.id
    ).count()

    return ApiResponse(
        success=True,
        detail="打卡日历",
        data={
            "year": year,
            "month": month,
            "days": calendar_days,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_checkin_days": total_checkins,
            "total_records": total_records,
        },
    )


@router.get("/achievements", response_model=ApiResponse)
def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()

    all_checked = (
        db.query(func.date(FoodRecord.recorded_at))
        .filter(FoodRecord.user_id == current_user.id)
        .distinct()
        .order_by(func.date(FoodRecord.recorded_at).desc())
        .all()
    )
    all_dates = [str(r[0]) for r in all_checked if r[0] is not None]

    current_streak = 0
    check_date = today
    while True:
        if check_date.strftime("%Y-%m-%d") in all_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            if check_date == today and today.strftime("%Y-%m-%d") not in all_dates:
                pass
            break

    longest_streak = 0
    temp_streak = 0
    sorted_dates = sorted(set(all_dates))
    for i, d_str in enumerate(sorted_dates):
        if i == 0:
            temp_streak = 1
        else:
            prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d").date()
            curr = datetime.strptime(d_str, "%Y-%m-%d").date()
            if (curr - prev).days == 1:
                temp_streak += 1
            else:
                temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak

    total_records = db.query(FoodRecord).filter(
        FoodRecord.user_id == current_user.id
    ).count()

    variety_count = (
        db.query(func.count(distinct(FoodRecord.food_name)))
        .filter(FoodRecord.user_id == current_user.id)
        .scalar()
    ) or 0

    profile = current_user.health_profile
    profile_complete = bool(
        profile and profile.height and profile.weight and profile.health_goal
    )

    stats = {
        "streak": current_streak,
        "longest_streak": longest_streak,
        "total_records": total_records,
        "food_variety": variety_count,
        "profile_complete": profile_complete,
    }

    results = []
    for ach in ACHIEVEMENTS:
        earned = False
        try:
            safe = {}
            safe["streak"] = stats["streak"]
            safe["longest_streak"] = stats["longest_streak"]
            safe["total_records"] = stats["total_records"]
            safe["food_variety"] = stats["food_variety"]
            safe["profile_complete"] = stats["profile_complete"]
            earned = eval(ach["condition"], {"__builtins__": {}}, safe)
        except Exception:
            earned = False

        results.append({
            "id": ach["id"],
            "name": ach["name"],
            "description": ach["description"],
            "icon": ach["icon"],
            "earned": earned,
        })

    earned_count = sum(1 for r in results if r["earned"])

    return ApiResponse(
        success=True,
        detail="成就列表",
        data={
            "achievements": results,
            "earned_count": earned_count,
            "total_count": len(results),
            "stats": stats,
        },
    )
