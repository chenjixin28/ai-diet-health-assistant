from pydantic import BaseModel, Field


class MealRecommendRequest(BaseModel):
    health_goal: str | None = None
    target_calories: int = Field(default=2000, ge=500, le=5000)
    preferences: str = ""


class NutritionSummaryItem(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbohydrates: float
    meal_count: int


class NutritionSummaryResponse(BaseModel):
    success: bool
    summary: list[NutritionSummaryItem]
