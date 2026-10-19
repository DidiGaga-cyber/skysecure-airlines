import json
import pika
from fpdf import FPDF
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import os

# Ustawienia połączenia
RABBITMQ_HOST = 'rabbitmq'
QUEUE_NAME = 'ticket_pdf_queue'
SAVE_DIR = '/app/pdfs'

# Upewnij się, że katalog zapisu istnieje
os.makedirs(SAVE_DIR, exist_ok=True)

def generate_pdf(ticket_data):
    """Funkcja do generowania pliku PDF z biletem"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Nagłówek
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="SkySecure Airlines - E-Ticket", ln=True, align='C')
    pdf.ln(10)
    
    # Dane biletu
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"ID Biletu: {ticket_data.get('ticket_id')}", ln=True)
    pdf.cell(200, 10, txt=f"Pasazer: {ticket_data.get('passenger_name')}", ln=True)
    pdf.cell(200, 10, txt=f"Numer lotu: {ticket_data.get('flight_number')}", ln=True)
    pdf.cell(200, 10, txt=f"Miejsce: {ticket_data.get('seat', 'Nieprzypisane')}", ln=True)
    
    # Zapis pliku
    file_name = f"ticket_{ticket_data.get('ticket_id')}.pdf"
    file_path = os.path.join(SAVE_DIR, file_name)
    pdf.output(file_path)
    print(f"[x] Pomyslnie wygenerowano plik PDF: {file_name}")

def callback(ch, method, properties, body):
    """Handler wiadomości przychodzących z kolejki"""
    try:
        print(f"[x] Otrzymano wiadomosc: {body.decode()}")
        ticket_data = json.loads(body)
        
        # Generowanie PDF
        generate_pdf(ticket_data)
        
        # Potwierdzenie pomyślnego przetworzenia (RabbitMQ usunie wiadomość z kolejki)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"[!] Blad podczas przetwarzania wiadomosci: {e}")
        # W przypadku błędu zwracamy wiadomość z powrotem do kolejki (Negative Acknowledgement)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Retry Pattern: Próba połączenia z RabbitMQ z opóźnieniem wykładniczym
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(10), # próbujemy aż do 10 razy, bo RabbitMQ długo wstaje
    retry=retry_if_exception_type(pika.exceptions.AMQPConnectionError)
)
def connect_and_consume():
    print("[*] Proba polaczenia z RabbitMQ...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    
    # Deklaracja trwałej kolejki
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    # Pobieranie tylko 1 zadania naraz
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    
    print(f"[*] Polaczono! Oczekiwanie na wiadomosci w kolejce '{QUEUE_NAME}'.")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        connect_and_consume()
    except KeyboardInterrupt:
        print("\n[*] Zatrzymywanie konsumenta...")
    except Exception as e:
        print(f"[!] Blad krytyczny: {e}")