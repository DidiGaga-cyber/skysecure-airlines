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
    current_user: models.User = Depends(get_current_user)
):
    # Lock flight row to prevent race conditions during booking
    flight = db.query(models.Flight).filter(
        models.Flight.id_lotu == reservation.id_lotu
    ).with_for_update().first() 

    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony")

    if flight.status != "Zaplanowany":
        raise HTTPException(
            status_code=400,
            detail=f"Nie można zarezerwować biletu na lot o statusie: {flight.status}"
        )

    if flight.liczba_miejsc <= 0:
        raise HTTPException(status_code=400, detail="Brak wolnych miejsc na ten lot")

    new_reservation = models.Rezerwacja(
        id_uzytkownika=current_user.id_uzytkownika,
        id_lotu=reservation.id_lotu,
        kwota_laczna=flight.cena
    )
    db.add(new_reservation)
    
    flight.liczba_miejsc -= 1

    audit_log = models.LogAudytowy(
        id_uzytkownika=current_user.id_uzytkownika,
        akcja="RESERVATION_CREATED",
        szczegoly=f"Utworzono rezerwację oczekującą na lot ID: {flight.id_lotu}"
    )
    db.add(audit_log)

    db.commit()
    db.refresh(new_reservation)

    return new_reservation
