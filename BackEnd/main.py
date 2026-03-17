from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from auth import router as auth_router

# Сначала БД
models.Base.metadata.create_all(bind=engine)

# Создаем приложение (добавляем root_path, чтобы Swagger не терялся за Nginx)
app = FastAPI(title="SkySecure Airlines API", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем авторизацию ОДИН РАЗ (префикс уже есть внутри auth.py)
app.include_router(auth_router)

# Базовый роутер для проверок
api_router = APIRouter()

@api_router.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "database": "connected"}

app.include_router(api_router)