from pydantic import BaseModel, Field


class FoodRecognizeResult(BaseModel):
    food_name: str
    confidence: float
    calories: float
    protein: float
    fat: float
    carbohydrates: float
    serving_size: str


class FoodRecognizeResponse(BaseModel):
    success: bool
    detail: str
    items: list[FoodRecognizeResult] = []


class FoodRecordCreate(BaseModel):
    food_name: str = Field(..., max_length=100)
    meal_type: str = Field(default="lunch", pattern="^(breakfast|lunch|dinner|snack)$")
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)
    carbohydrates: float = Field(..., ge=0)
    serving_size: str | None = None
    image_url: str | None = None


class FoodSearchQuery(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=50)
