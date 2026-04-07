from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
import models, schemas
from database import get_db

router = APIRouter(prefix="/flights", tags=["flights"])

@router.get("/", response_model=List[schemas.FlightOut])
def get_flights(
    origin: Optional[str] = Query(None, alias="from", description="City or IATA code of departure"),
    destination: Optional[str] = Query(None, alias="to", description="City or IATA code of arrival"),
    departure_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db)
):
    # Создаем базовый запрос с JOIN, чтобы видеть данные аэропортов
    # Мы используем алиасы (aliased), если нужно разделять аэропорт вылета и прилета
    from sqlalchemy.orm import aliased
    
    AirportOrigin = aliased(models.Airport)
    AirportDest = aliased(models.Airport)

    query = db.query(models.Flight).join(
        AirportOrigin, models.Flight.id_lotniska_odlotu == AirportOrigin.id_lotniska
    ).join(
        AirportDest, models.Flight.id_lotniska_przylotu == AirportDest.id_lotniska
    )

    # Фильтр по городу или коду IATA вылета
    if origin:
        query = query.filter(
            (AirportOrigin.miasto.ilike(f"%{origin}%")) | 
            (AirportOrigin.kod_iata.ilike(f"{origin}"))
        )
    
    # Фильтр по городу или коду IATA прилета
    if destination:
        query = query.filter(
            (AirportDest.miasto.ilike(f"%{destination}%")) | 
            (AirportDest.kod_iata.ilike(f"{destination}"))
        )
        
    # Фильтр по дате (теперь поле называется czas_odlotu)
    if departure_date:
        query = query.filter(func.date(models.Flight.czas_odlotu) == departure_date)

    return query.all()

@router.get("/{id_lotu}/seats", response_model=List[schemas.SeatOut])
def get_flight_seats(id_lotu: int, db: Session = Depends(get_db)):
    """
    Возвращает список всех мест для конкретного рейса с их статусом (свободно/занято).
    """
    # 1. Проверяем, существует ли такой рейс вообще
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony")

    # 2. Получаем все места из таблицы Miejsca для этого рейса
    # В моделях этот класс называется Miejsce (судя по твоему файлу tickets.py)
    seats = db.query(models.Miejsce).filter(models.Miejsce.id_lotu == id_lotu).order_by(models.Miejsce.id_miejsca).all()
    
    # 3. Если мест в базе нет (например, рейс создан, но скрипт генерации мест не запущен)
    if not seats:
        return []

    return seats