from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from auth import router as auth_router
from flights import router as flights_router
from bookings import router as bookings_router
from tickets import router as tickets_router
from payments import router as payments_router

# Сначала БД
models.Base.metadata.create_all(bind=engine)

# Создаем приложение (root_path нужен, чтобы Swagger не терялся за Nginx)
app = FastAPI(title="SkySecure Airlines API", root_path="/api")

# -------------------------------------------------------
# CORS — разрешаем только наш фронтенд (не "*")
# При деплое замените localhost на реальный домен
# -------------------------------------------------------
origins = [
    "https://localhost",
    "https://127.0.0.1",
    "http://localhost",       #  для dev-режима
    "http://127.0.0.1",       #  для dev-режима
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Подключаем роутеры
app.include_router(auth_router)

api_router = APIRouter()

@api_router.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "database": "connected"}

app.include_router(api_router)
app.include_router(flights_router)
app.include_router(bookings_router)
app.include_router(tickets_router)
app.include_router(payments_router)