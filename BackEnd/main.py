from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base

# Создаем таблицы в БД (хотя моделей пока нет, это создаст пустую базу)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkySecure Airlines API",
    description="API for flight booking and management",
    version="0.1.0"
)

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Простой эндпоинт для проверки статуса сервера
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok", "message": "API and Database connection are working!"}