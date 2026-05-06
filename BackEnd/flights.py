from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
import models, schemas
from database import get_db
from auth import get_current_user

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


# ---------------------------------------------------------------------------
# Helper: enforce Admin role
# ---------------------------------------------------------------------------

def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Raises 403 if the authenticated user is not an Admin."""
    if current_user.rola != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień. Wymagana rola: Admin.",
        )
    return current_user


# ---------------------------------------------------------------------------
# ADMIN-ONLY endpoints
# ---------------------------------------------------------------------------

@router.post("/", response_model=schemas.FlightOut, status_code=status.HTTP_201_CREATED)
def create_flight(
    flight_data: schemas.FlightCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """
    [ADMIN] Dodaj nowy lot.
    Wymaga tokena JWT z rolą Admin.
    """
    # Validate airports exist
    if not db.query(models.Airport).filter(models.Airport.id_lotniska == flight_data.id_lotniska_odlotu).first():
        raise HTTPException(status_code=404, detail=f"Lotnisko odlotu (id={flight_data.id_lotniska_odlotu}) nie istnieje.")
    if not db.query(models.Airport).filter(models.Airport.id_lotniska == flight_data.id_lotniska_przylotu).first():
        raise HTTPException(status_code=404, detail=f"Lotnisko przylotu (id={flight_data.id_lotniska_przylotu}) nie istnieje.")

    # Validate flight times
    if flight_data.czas_przylotu <= flight_data.czas_odlotu:
        raise HTTPException(status_code=400, detail="Czas przylotu musi być późniejszy niż czas odlotu.")

    # Ensure unique flight number
    if db.query(models.Flight).filter(models.Flight.numer_lotu == flight_data.numer_lotu).first():
        raise HTTPException(status_code=409, detail=f"Lot o numerze '{flight_data.numer_lotu}' już istnieje.")

    new_flight = models.Flight(**flight_data.model_dump())
    db.add(new_flight)
    db.commit()
    db.refresh(new_flight)
    return new_flight


@router.put("/{id_lotu}", response_model=schemas.FlightOut)
def update_flight(
    id_lotu: int,
    flight_data: schemas.FlightUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """
    [ADMIN] Zaktualizuj dane lotu (częściowa aktualizacja).
    Wymaga tokena JWT z rolą Admin.
    """
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony.")

    update_dict = flight_data.model_dump(exclude_unset=True)

    if "id_lotniska_odlotu" in update_dict:
        if not db.query(models.Airport).filter(models.Airport.id_lotniska == update_dict["id_lotniska_odlotu"]).first():
            raise HTTPException(status_code=404, detail="Nowe lotnisko odlotu nie istnieje.")
    if "id_lotniska_przylotu" in update_dict:
        if not db.query(models.Airport).filter(models.Airport.id_lotniska == update_dict["id_lotniska_przylotu"]).first():
            raise HTTPException(status_code=404, detail="Nowe lotnisko przylotu nie istnieje.")

    # Validate time consistency after update
    new_odlot = update_dict.get("czas_odlotu", flight.czas_odlotu)
    new_przylot = update_dict.get("czas_przylotu", flight.czas_przylotu)
    if new_przylot <= new_odlot:
        raise HTTPException(status_code=400, detail="Czas przylotu musi być późniejszy niż czas odlotu.")

    for field, value in update_dict.items():
        setattr(flight, field, value)

    db.commit()
    db.refresh(flight)
    return flight


@router.delete("/{id_lotu}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight(
    id_lotu: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """
    [ADMIN] Usuń lot.
    Uwaga: CASCADE w bazie usunie powiązane miejsca i rezerwacje.
    Wymaga tokena JWT z rolą Admin.
    """
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony.")

    if flight.status == "W trakcie":
        raise HTTPException(
            status_code=409,
            detail="Nie można usunąć lotu w trakcie realizacji. Najpierw zmień status.",
        )

    db.delete(flight)
    db.commit()