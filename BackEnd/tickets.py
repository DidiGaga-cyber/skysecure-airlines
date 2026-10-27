import json
import pika
import os
import time
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from auth import get_current_user

DB_ENCRYPTION_KEY = os.environ.get("DB_ENCRYPTION_KEY")
if not DB_ENCRYPTION_KEY:
    raise ValueError("Brak klucza szyfrowania DB_ENCRYPTION_KEY w .env!")

router = APIRouter(prefix="/tickets", tags=["tickets"])

def send_pdf_task_to_queue(ticket_data: dict):
    """Wysyła zadanie generowania PDF do RabbitMQ (Architektura SOA)"""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='ticket_pdf_queue', durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key='ticket_pdf_queue',
            body=json.dumps(ticket_data),
            properties=pika.BasicProperties(
                delivery_mode=2, # Wiadomości są trwałe (nie znikną po restarcie)
            )
        )
        connection.close()
        print(f"[RabbitMQ] Zadanie dla biletu {ticket_data.get('ticket_id')} wysłane do kolejki.")
    except Exception as e:
        print(f"[RabbitMQ] Błąd połączenia: {e}")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Проверка бронирования
    rezerwacja = db.query(models.Rezerwacja).filter(
        models.Rezerwacja.id_rezerwacji == ticket.id_rezerwacji,
        models.Rezerwacja.id_uzytkownika == current_user.id_uzytkownika
    ).first()
    
    if not rezerwacja:
        raise HTTPException(status_code=404, detail="Rezerwacja nie znaleziona lub brak dostępu")

    # 2. Блокировка места
    miejsce = db.query(models.Miejsce).filter(
        models.Miejsce.id_miejsca == ticket.id_miejsca,
        models.Miejsce.czy_wolne == True
    ).with_for_update().first()

    if not miejsce:
        raise HTTPException(status_code=400, detail="Wybrane miejsce jest już zajęte")

    # Вытягиваем данные о рейсе для передачи в микросервис
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == miejsce.id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony")
    if flight.status != "Zaplanowany":
        raise HTTPException(
            status_code=400,
            detail=f"Nie można wystawić biletu na lot o statusie: {flight.status}"
        )
    if miejsce.id_lotu != rezerwacja.id_lotu:
        raise HTTPException(status_code=400, detail="Wybrane miejsce nie należy do zarezerwowanego lotu")
    flight_number = flight.numer_lotu

    # 3. Создание билета
    new_ticket = models.Bilet(
        id_rezerwacji=ticket.id_rezerwacji,
        id_miejsca=ticket.id_miejsca,
        imie_pasazera=ticket.imie,
        nazwisko_pasazera=ticket.nazwisko,
    )
    db.add(new_ticket)

    # 4. Обновление статуса места
    miejsce.czy_wolne = False
    
    # 5. Логирование (Security Audit)
    audit_log = models.LogAudytowy(
        id_uzytkownika=current_user.id_uzytkownika,
        akcja="TICKET_ISSUED",
        szczegoly=f"Wystawiono bilet dla rezerwacji {ticket.id_rezerwacji}, miejsce {ticket.id_miejsca}"
    )
    db.add(audit_log)

    db.commit()
    db.refresh(new_ticket)

    # 6. SOA & Message Broker: Отправляем асинхронную задачу в RabbitMQ
    ticket_data = {
        "ticket_id": new_ticket.id_biletu,
        "passenger_name": f"{new_ticket.imie_pasazera} {new_ticket.nazwisko_pasazera}",
        "flight_number": flight_number,
        "seat": miejsce.numer_miejsca
    }
    send_pdf_task_to_queue(ticket_data)

    return {
        "status": "success",
        "message": "Bilet wygenerowany. Plik PDF jest przygotowywany w tle.",
        "id_bileta": new_ticket.id_biletu 
    }

@router.get("/{id_bileta}/pdf")
def get_ticket_pdf(id_bileta: int):
    file_path = f"/app/pdfs/ticket_{id_bileta}.pdf"
    
    # Ждем до 5 секунд, пока микросервис (RabbitMQ consumer) создаст файл
    for _ in range(10):
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                media_type="application/pdf",
                filename=f"ticket_{id_bileta}.pdf"
            )
        time.sleep(0.5)
        
    # Если файл не успел сгенерироваться за 5 секунд
    raise HTTPException(
        status_code=404, 
        detail="PDF wciąż się generuje. Odśwież stronę za chwilę."
    )
