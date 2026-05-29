import os
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, File, UploadFile, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.food_record import FoodRecord
from app.schemas.food import (
    FoodRecognizeResponse,
    FoodRecognizeResult,
    FoodRecordCreate,
    FoodSearchQuery,
)
from app.schemas.user import ApiResponse
from app.services.food_recognition import predict_food_from_image
from app.services.nutrition_calculator import search_food_by_name
from app.api.deps import get_current_user

router = APIRouter(prefix="/foods", tags=["食物识别"])

settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/recognize", response_model=FoodRecognizeResponse)
async def recognize_food_image(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        return FoodRecognizeResponse(success=False, detail="仅支持 JPG / PNG / WEBP 格式")

    file_data = await image.read()
    if len(file_data) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        return FoodRecognizeResponse(success=False, detail=f"图片不能超过 {settings.MAX_UPLOAD_SIZE_MB}MB")

    ext = os.path.splitext(image.filename or "image.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = settings.UPLOAD_DIR / filename
    filepath.write_bytes(file_data)

    items = predict_food_from_image(str(filepath))

    return FoodRecognizeResponse(
        success=True,
        detail=f"识别到 {len(items)} 种食物",
        items=[FoodRecognizeResult(**item) for item in items],
    )


@router.post("/record", response_model=ApiResponse)
def add_food_record(
    payload: FoodRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = FoodRecord(
        user_id=current_user.id,
        food_name=payload.food_name,
        meal_type=payload.meal_type,
        calories=payload.calories,
        protein=payload.protein,
        fat=payload.fat,
        carbohydrates=payload.carbohydrates,
        serving_size=payload.serving_size,
        image_url=payload.image_url,
        recorded_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ApiResponse(
        success=True,
        detail="食物记录已添加",
        data={"id": record.id, "food_name": record.food_name},
    )


@router.get("/records", response_model=ApiResponse)
def get_food_records(
    date: str | None = Query(None, description="日期 YYYY-MM-DD"),
    meal_type: str | None = Query(None, description="餐次"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime as dt

    query = db.query(FoodRecord).filter(FoodRecord.user_id == current_user.id)

    if date:
        try:
            d = dt.strptime(date, "%Y-%m-%d")
            nxt = dt(d.year, d.month, d.day) + timedelta(days=1)
            query = query.filter(FoodRecord.recorded_at >= d, FoodRecord.recorded_at < nxt)
        except ValueError:
            pass

    if meal_type:
        query = query.filter(FoodRecord.meal_type == meal_type)

    records = query.order_by(FoodRecord.recorded_at.desc()).all()

    return ApiResponse(
        success=True,
        detail="查询成功",
        data={
            "records": [
                {
                    "id": r.id,
                    "food_name": r.food_name,
                    "meal_type": r.meal_type,
                    "calories": r.calories,
                    "protein": r.protein,
                    "fat": r.fat,
                    "carbohydrates": r.carbohydrates,
                    "serving_size": r.serving_size,
                    "image_url": r.image_url,
                    "recorded_at": r.recorded_at.isoformat(),
                }
                for r in records
            ]
        },
    )


@router.post("/search", response_model=ApiResponse)
def search_food(
    payload: FoodSearchQuery,
    current_user: User = Depends(get_current_user),
):
    results = search_food_by_name(payload.keyword)
    return ApiResponse(
        success=True,
        detail=f"找到 {len(results)} 个结果",
        data={"foods": results},
    )
