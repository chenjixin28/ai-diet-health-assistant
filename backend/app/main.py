from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import init_db
from app.models import User, HealthProfile, FoodRecord, NutritionLog, MealPlan
from app.api.v1.auth import router as auth_router
from app.api.v1.foods import router as foods_router
from app.api.v1.nutrition import router as nutrition_router
from app.api.v1.checkin import router as checkin_router
from app.utils.exceptions import (
    AppError,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(foods_router, prefix=settings.API_V1_PREFIX)
app.include_router(nutrition_router, prefix=settings.API_V1_PREFIX)
app.include_router(checkin_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI饮食健康助手运行中"}
