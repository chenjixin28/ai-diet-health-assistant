from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import HealthGoal


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("用户名只能包含字母、数字、下划线和连字符")
        return v.strip()


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., min_length=1, description="密码")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    height: float | None = None
    weight: float | None = None
    health_goal: HealthGoal | None = None
    target_weight: float | None = None
    daily_calorie_target: int | None = None
    daily_protein_target: float | None = None
    daily_fat_target: float | None = None
    daily_carb_target: float | None = None

    model_config = {"from_attributes": True}


class HealthProfileUpdate(BaseModel):
    height: float | None = Field(None, gt=0, le=300, description="身高 (cm)")
    weight: float | None = Field(None, gt=0, le=500, description="体重 (kg)")
    health_goal: HealthGoal | None = None
    target_weight: float | None = Field(None, gt=0, le=500, description="目标体重 (kg)")
    daily_calorie_target: int | None = Field(None, ge=0, description="每日热量目标 (kcal)")
    daily_protein_target: float | None = Field(None, ge=0, description="每日蛋白质目标 (g)")
    daily_fat_target: float | None = Field(None, ge=0, description="每日脂肪目标 (g)")
    daily_carb_target: float | None = Field(None, ge=0, description="每日碳水目标 (g)")


class ApiResponse(BaseModel):
    success: bool
    detail: str = ""
    data: dict | list | None = None
