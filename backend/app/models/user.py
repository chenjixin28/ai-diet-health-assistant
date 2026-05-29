from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class HealthGoal(str, enum.Enum):
    LOSE_FAT = "lose_fat"
    BUILD_MUSCLE = "build_muscle"
    CONTROL_SUGAR = "control_sugar"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    health_profile = relationship("HealthProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    food_records = relationship("app.models.food_record.FoodRecord", back_populates="user", cascade="all, delete-orphan")
    nutrition_logs = relationship("app.models.food_record.NutritionLog", back_populates="user", cascade="all, delete-orphan")


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    height = Column(Float, nullable=True, comment="身高 (cm)")
    weight = Column(Float, nullable=True, comment="体重 (kg)")
    health_goal = Column(Enum(HealthGoal), nullable=True)
    target_weight = Column(Float, nullable=True, comment="目标体重 (kg)")
    daily_calorie_target = Column(Integer, nullable=True, comment="每日目标热量 (kcal)")
    daily_protein_target = Column(Float, nullable=True, comment="每日目标蛋白质 (g)")
    daily_fat_target = Column(Float, nullable=True, comment="每日目标脂肪 (g)")
    daily_carb_target = Column(Float, nullable=True, comment="每日目标碳水 (g)")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="health_profile")
