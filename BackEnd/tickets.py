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

PDF_DIR = "/app/pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

router = APIRouter(prefix="/tickets", tags=["tickets"])


def send_pdf_task_to_queue(ticket_data: dict) -> bool:
    # Enqueue PDF generation task in RabbitMQ
    try:
        params = pika.ConnectionParameters(
            host='rabbitmq',
            connection_attempts=2,
            retry_delay=1,
            socket_timeout=2,
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='ticket_pdf_queue', durable=True)

        channel.basic_publish(
            exchange='',
            routing_key='ticket_pdf_queue',
            body=json.dumps(ticket_data),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        connection.close()
        return True
    except Exception as e:
        print(f"[RabbitMQ] Connection error (task buffered): {e}")
        return False


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    rezerwacja = db.query(models.Rezerwacja).filter(
        models.Rezerwacja.id_rezerwacji == ticket.id_rezerwacji,
        models.Rezerwacja.id_uzytkownika == current_user.id_uzytkownika
    ).first()

    if not rezerwacja:
        raise HTTPException(status_code=404, detail="Rezerwacja nie znaleziona lub brak dostępu")

    # Lock seat row to prevent double booking
    miejsce = db.query(models.Miejsce).filter(
        models.Miejsce.id_miejsca == ticket.id_miejsca,
        models.Miejsce.czy_wolne == True
    ).with_for_update().first()

    if not miejsce:
        raise HTTPException(status_code=400, detail="Wybrane miejsce jest już zajęte")

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

    new_ticket = models.Bilet(
        id_rezerwacji=ticket.id_rezerwacji,
        id_miejsca=ticket.id_miejsca,
        imie_pasazera=ticket.imie,
        nazwisko_pasazera=ticket.nazwisko,
    )
    db.add(new_ticket)

    miejsce.czy_wolne = False

    audit_log = models.LogAudytowy(
        id_uzytkownika=current_user.id_uzytkownika,
        akcja="TICKET_ISSUED",
        szczegoly=f"Wystawiono bilet dla rezerwacji {ticket.id_rezerwacji}, miejsce {ticket.id_miejsca}"
    )
    db.add(audit_log)

    db.commit()
    db.refresh(new_ticket)

    # Remove any stale PDF from a previous database session with the same ticket ID
    pdf_path = os.path.join(PDF_DIR, f"ticket_{new_ticket.id_biletu}.pdf")
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except OSError:
            pass

    ticket_data = {
        "ticket_id": new_ticket.id_biletu,
        "passenger_name": f"{new_ticket.imie_pasazera} {new_ticket.nazwisko_pasazera}",
        "flight_number": flight_number,
        "seat": miejsce.numer_miejsca
    }

    # Buffer task metadata locally in case RabbitMQ is temporarily down
    buffer_path = os.path.join(PDF_DIR, f"ticket_{new_ticket.id_biletu}.json")
    try:
        with open(buffer_path, "w", encoding="utf-8") as f:
            json.dump(ticket_data, f)
    except OSError:
        pass

    if send_pdf_task_to_queue(ticket_data):
        try:
            if os.path.exists(buffer_path):
                os.remove(buffer_path)
        except OSError:
            pass

    return {
        "status": "success",
        "message": "Bilet wygenerowany. Plik PDF jest przygotowywany w tle.",
        "id_bileta": new_ticket.id_biletu
    }


@router.get("/{id_bileta}/pdf")
def get_ticket_pdf(id_bileta: int):
    file_path = os.path.join(PDF_DIR, f"ticket_{id_bileta}.pdf")
    buffer_path = os.path.join(PDF_DIR, f"ticket_{id_bileta}.json")

    # If PDF is not generated yet and a buffered task exists (e.g., RabbitMQ was down during booking), retry sending it
    if not os.path.exists(file_path) and os.path.exists(buffer_path):
        try:
            with open(buffer_path, "r", encoding="utf-8") as f:
                buffered_data = json.load(f)
            if send_pdf_task_to_queue(buffered_data):
                try:
                    os.remove(buffer_path)
                except OSError:
                    pass
        except Exception:
            pass

    # Wait up to 5 seconds for background worker to create PDF
    for _ in range(10):
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                media_type="application/pdf",
                filename=f"ticket_{id_bileta}.pdf"
            )
        time.sleep(0.5)

    raise HTTPException(
        status_code=404,
        detail="PDF wciąż się generuje. Odśwież stronę za chwilę."
    )
