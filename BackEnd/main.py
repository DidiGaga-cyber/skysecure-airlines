from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import engine

app = FastAPI(title="SkySecure Airlines API")

# Настройка CORS, чтобы Vue.js (Axios) мог отправлять запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничим до конкретного домена
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем роутер с обязательным префиксом /api
api_router = APIRouter(prefix="/api")

@api_router.get("/health")
def health_check():
    return {
        "status": "ok", 
        "message": "SkySecure Backend is running on PostgreSQL",
        "database": "connected"
    }

# Подключаем роутер к основному приложению
app.include_router(api_router)