import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/process", response_model=schemas.PaymentOut, status_code=status.HTTP_200_OK)
def process_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    rezerwacja = db.query(models.Rezerwacja).filter(
        models.Rezerwacja.id_rezerwacji == payment.id_rezerwacji,
        models.Rezerwacja.id_uzytkownika == current_user.id_uzytkownika
    ).first()

    if not rezerwacja:
        raise HTTPException(status_code=404, detail="Rezerwacja nie znaleziona")

    if rezerwacja.status == "Opłacona":
        raise HTTPException(status_code=400, detail="Ta rezerwacja została już opłacona")
    if rezerwacja.status == "Anulowana":
        raise HTTPException(status_code=400, detail="Nie można opłacić anulowanej rezerwacji")

    flight = db.query(models.Flight).filter(models.Flight.id_lotu == rezerwacja.id_lotu).first()
    if flight and flight.status != "Zaplanowany":
        raise HTTPException(
            status_code=400,
            detail=f"Nie można opłacić rezerwacji na lot o statusie: {flight.status}"
        )

    # Simulated transaction success
    sesja_uuid = uuid.uuid4()
    symulowany_status = "Success"

    nowa_platnosc = models.Platnosc(
        id_rezerwacji=rezerwacja.id_rezerwacji,
        kwota=rezerwacja.kwota_laczna,
        status_transakcji=symulowany_status,
        metoda=payment.metoda,
        identyfikator_sesji=sesja_uuid
    )
    db.add(nowa_platnosc)

    rezerwacja.status = "Opłacona"

    audit_log = models.LogAudytowy(
        id_uzytkownika=current_user.id_uzytkownika,
        akcja="PAYMENT_SUCCESS",
        szczegoly=f"Zaksięgowano płatność {rezerwacja.kwota_laczna} PLN metodą {payment.metoda} dla rezerwacji {rezerwacja.id_rezerwacji}"
    )
    db.add(audit_log)

    db.commit()
    db.refresh(nowa_platnosc)

    return nowa_platnosc
