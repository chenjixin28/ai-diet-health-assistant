from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class FoodRecord(Base):
    __tablename__ = "food_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_name = Column(String(100), nullable=False, comment="食物名称")
    meal_type = Column(String(20), nullable=False, default="lunch", comment="餐次：breakfast/lunch/dinner/snack")
    image_url = Column(String(500), nullable=True, comment="食物图片URL")
    calories = Column(Float, nullable=False, default=0, comment="热量 (kcal)")
    protein = Column(Float, nullable=False, default=0, comment="蛋白质 (g)")
    fat = Column(Float, nullable=False, default=0, comment="脂肪 (g)")
    carbohydrates = Column(Float, nullable=False, default=0, comment="碳水 (g)")
    serving_size = Column(String(50), nullable=True, comment="份量描述")
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("app.models.user.User", back_populates="food_records")


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    log_date = Column(DateTime, nullable=False, index=True, comment="日志日期")
    total_calories = Column(Float, nullable=False, default=0, comment="总热量 (kcal)")
    total_protein = Column(Float, nullable=False, default=0, comment="总蛋白质 (g)")
    total_fat = Column(Float, nullable=False, default=0, comment="总脂肪 (g)")
    total_carbohydrates = Column(Float, nullable=False, default=0, comment="总碳水 (g)")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("app.models.user.User", back_populates="nutrition_logs")
