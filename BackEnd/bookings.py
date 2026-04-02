from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=schemas.ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation: schemas.ReservationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Требует авторизации!
):
    # 1. Проверяем, существует ли рейс
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == reservation.id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony")

    # 2. Проверяем, есть ли свободные места
    if flight.liczba_miejsc <= 0:
        raise HTTPException(status_code=400, detail="Brak wolnych miejsc na ten lot")

    # 3. Уменьшаем количество доступных мест
    flight.liczba_miejsc -= 1

    # 4. Создаем бронирование. Статус "Oczekująca" проставится автоматически БД
    new_reservation = models.Rezerwacja(
        id_uzytkownika=current_user.id_uzytkownika,
        id_lotu=reservation.id_lotu
    )

    db.add(new_reservation)
    
    # Можно сразу добавить лог действий пользователя (Audyt)
    audit_log = models.LogAudytowy(
        id_uzytkownika=current_user.id_uzytkownika,
        akcja="RESERVATION_CREATED",
        szczegoly=f"Utworzono rezerwację oczekującą na lot ID: {flight.id_lotu}"
    )
    db.add(audit_log)

    db.commit()
    db.refresh(new_reservation)

    return new_reservation