import io
import base64
import qrcode
import os
from jinja2 import Template
from weasyprint import HTML
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, status, Response
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

TICKET_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page { size: A4; margin: 0; }
        body { font-family: sans-serif; background-color: #f4f4f4; padding: 40px; }
        .ticket { background: white; border: 2px solid #2c3e50; border-radius: 15px; display: flex; overflow: hidden; min-height: 250px; }
        .info { padding: 30px; flex: 3; }
        .qr-section { background: #2c3e50; padding: 30px; display: flex; align-items: center; justify-content: center; flex: 1; }
        .qr-section img { background: white; padding: 10px; border-radius: 5px; }
        h1 { margin: 0; color: #2c3e50; font-size: 28px; }
        .route { font-size: 24px; font-weight: bold; margin: 15px 0; color: #e67e22; }
        .details { font-size: 14px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="ticket">
        <div class="info">
            <h1>SkySecure Airlines</h1>
            <div class="route">{{ origin }} → {{ destination }}</div>
            <p><strong>Pasażer:</strong> {{ first_name }} {{ last_name }}</p>
            <p><strong>Lot:</strong> {{ flight_number }} | <strong>Miejsce:</strong> {{ seat_number }}</p>
            <div class="details">Data odlotu: {{ departure_time }}</div>
        </div>
        <div class="qr-section">
            <img src="data:image/png;base64,{{ qr_code }}" width="140">
        </div>
    </div>
</body>
</html>
"""

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
        # dane_paszportowe=func.pgp_sym_encrypt(ticket.paszport, DB_ENCRYPTION_KEY, 'cipher-algo=aes256') # Убрано, так как паспортные данные больше не требуются для бронирования
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
    
    return {"status": "success", "message": "Bilet wygenerowany"}

@router.get("/{id_bileta}/pdf")
def get_ticket_pdf(
    id_bileta: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # 1. Собираем все данные для билета через JOIN
    ticket_data = db.query(
        models.Bilet,
        models.Miejsce.numer_miejsca,
        models.Flight.numer_lotu,
        models.Flight.czas_odlotu,
        models.Flight.id_lotniska_odlotu.label("origin"),
        models.Flight.id_lotniska_przylotu.label("destination")
    ).join(models.Miejsce, models.Bilet.id_miejsca == models.Miejsce.id_miejsca)\
     .join(models.Flight, models.Miejsce.id_lotu == models.Flight.id_lotu)\
     .filter(models.Bilet.id_bileta == id_bileta).first()

    if not ticket_data:
        raise HTTPException(status_code=404, detail="Bilet nie znaleziony")

    # 2. Генерируем QR-код (содержит ссылку или ID для проверки)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"TICKET-ID: {id_bileta}") # Тут может быть ссылка на проверку
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    # 3. Рендерим HTML через Jinja2
    with open("ticket_template.html", "r") as f:
        template = Template(f.read())
    
    html_out = template.render(
        origin=ticket_data.origin,
        destination=ticket_data.destination,
        first_name=ticket_data.Bilet.imie_pasazera,
        last_name=ticket_data.Bilet.nazwisko_pasazera,
        flight_number=ticket_data.numer_lotu,
        seat_number=ticket_data.numer_miejsca,
        departure_time=ticket_data.czas_odlotu.strftime("%d.%m.%Y %H:%M"),
        qr_code=qr_base64
    )

    # 4. Конвертируем HTML в PDF
    pdf_file = HTML(string=html_out).write_pdf()

    # 5. Возвращаем как файл для скачивания
    return Response(
        content=pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ticket_{id_bileta}.pdf"}
    )