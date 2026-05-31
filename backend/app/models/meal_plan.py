from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal_type = Column(String(32), nullable=False, index=True, comment="目标: lose_fat / build_muscle / control_sugar")
    breakfast = Column(String(500), nullable=False, comment="早餐")
    lunch = Column(String(500), nullable=False, comment="午餐")
    dinner = Column(String(500), nullable=False, comment="晚餐")
    snack = Column(String(500), nullable=False, comment="加餐")
    total_calories = Column(Integer, nullable=False, default=0, comment="总热量估算")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
