from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, HealthProfile
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserProfileResponse,
    HealthProfileUpdate,
    ApiResponse,
)
from app.utils.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        return ApiResponse(
            success=False,
            detail="用户名已被注册",
        )
    if db.query(User).filter(User.email == payload.email).first():
        return ApiResponse(
            success=False,
            detail="邮箱已被注册",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()

    health_profile = HealthProfile(user_id=user.id)
    db.add(health_profile)
    db.commit()
    db.refresh(user)

    return ApiResponse(
        success=True,
        detail="注册成功",
        data={"user_id": user.id, "username": user.username},
    )


@router.post("/login", response_model=ApiResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.username)
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        return ApiResponse(
            success=False,
            detail="用户名或密码错误",
        )

    if not user.is_active:
        return ApiResponse(
            success=False,
            detail="账户已被禁用",
        )

    token = create_access_token(data={"user_id": user.id, "username": user.username})
    return ApiResponse(
        success=True,
        detail="登录成功",
        data={
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
        },
    )


@router.get("/me", response_model=ApiResponse)
def get_me(current_user: User = Depends(get_current_user)):
    profile = current_user.health_profile
    return ApiResponse(
        success=True,
        detail="获取用户信息成功",
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active,
            "height": profile.height if profile else None,
            "weight": profile.weight if profile else None,
            "health_goal": profile.health_goal.value if profile and profile.health_goal else None,
            "target_weight": profile.target_weight if profile else None,
            "daily_calorie_target": profile.daily_calorie_target if profile else None,
            "daily_protein_target": profile.daily_protein_target if profile else None,
            "daily_fat_target": profile.daily_fat_target if profile else None,
            "daily_carb_target": profile.daily_carb_target if profile else None,
        },
    )


@router.put("/profile", response_model=ApiResponse)
def update_profile(
    payload: HealthProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = current_user.health_profile
    if profile is None:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return ApiResponse(
        success=True,
        detail="健康档案更新成功",
    )
