import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from database import get_db
from auth import get_current_user

# Вытягиваем ключ из окружения. Fail-safe: если ключа нет, приложение не запустится.
DB_ENCRYPTION_KEY = os.environ.get("DB_ENCRYPTION_KEY")
if not DB_ENCRYPTION_KEY:
    raise ValueError("Brak klucza szyfrowania DB_ENCRYPTION_KEY w .env!")

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Проверяем, существует ли бронирование и принадлежит ли оно текущему пользователю
    rezerwacja = db.query(models.Rezerwacja).filter(
        models.Rezerwacja.id_rezerwacji == ticket.id_rezerwacji,
        models.Rezerwacja.id_uzytkownika == current_user.id_uzytkownika
    ).first()
    
    if not rezerwacja:
        raise HTTPException(status_code=404, detail="Rezerwacja nie znaleziona lub brak dostępu")

    # 2. Блокируем место для проверки (защита от двойной покупки)
    miejsce = db.query(models.Miejsce).filter(
        models.Miejsce.id_miejsca == ticket.id_miejsca,
        models.Miejsce.czy_wolne == True
    ).with_for_update().first()

    if not miejsce:
        raise HTTPException(status_code=400, detail="Wybrane miejsce jest już zajęte")

    # 3. Создаем билет и ШИФРУЕМ паспорт
    new_ticket = models.Bilet(
        id_rezerwacji=ticket.id_rezerwacji,
        id_miejsca=ticket.id_miejsca,
        imie_pasazera=ticket.imie,
        nazwisko_pasazera=ticket.nazwisko,
        # Магия pgcrypto: вызываем функцию БД с явным указанием AES-256
        dane_paszportowe=func.pgp_sym_encrypt(ticket.paszport, DB_ENCRYPTION_KEY, 'cipher-algo=aes256')
    )
    db.add(new_ticket)

    # 4. Отмечаем место как занятое
    miejsce.czy_wolne = False
    
    # 5. Логируем действие (Security Audit)
    audit_log = models.LogAudytowy(
        id_uzytkownika=current_user.id_uzytkownika,
        akcja="TICKET_ISSUED",
        szczegoly=f"Wystawiono bilet dla rezerwacji {ticket.id_rezerwacji}, miejsce {ticket.id_miejsca}"
    )
    db.add(audit_log)

    db.commit()
    
    return {"status": "success", "message": "Bilet wygenerowany, dane paszportowe zabezpieczone algorytmem AES-256"}