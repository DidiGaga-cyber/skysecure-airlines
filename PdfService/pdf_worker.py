import json
import os
import time
import pika
from fpdf import FPDF
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

RABBITMQ_HOST = 'rabbitmq'
QUEUE_NAME = 'ticket_pdf_queue'
SAVE_DIR = '/app/pdfs'

os.makedirs(SAVE_DIR, exist_ok=True)


def log_retry(retry_state):
    exc = retry_state.outcome.exception()
    wait_time = retry_state.next_action.sleep
    print(
        f"[!] Connection to RabbitMQ failed ({exc}). "
        f"Retrying in {wait_time:.1f}s (Attempt {retry_state.attempt_number}/10)..."
    )


def generate_pdf(ticket_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="SkySecure Airlines - E-Ticket", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"ID Biletu: {ticket_data.get('ticket_id')}", ln=True)
    pdf.cell(200, 10, txt=f"Pasazer: {ticket_data.get('passenger_name')}", ln=True)
    pdf.cell(200, 10, txt=f"Numer lotu: {ticket_data.get('flight_number')}", ln=True)
    pdf.cell(200, 10, txt=f"Miejsce: {ticket_data.get('seat', 'Nieprzypisane')}", ln=True)

    file_name = f"ticket_{ticket_data.get('ticket_id')}.pdf"
    file_path = os.path.join(SAVE_DIR, file_name)
    pdf.output(file_path)
    print(f"[x] Successfully generated PDF: {file_name}")


def callback(ch, method, properties, body):
    try:
        print(f"[x] Received message: {body.decode()}")
        ticket_data = json.loads(body)
        generate_pdf(ticket_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[!] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


# Retry connection with exponential backoff (handles both AMQP errors and DNS/socket errors when container is stopped)
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(10),
    retry=retry_if_exception_type((pika.exceptions.AMQPError, OSError)),
    before_sleep=log_retry,
    reraise=True,
)
def connect_and_consume():
    print(f"[*] Attempting to connect to RabbitMQ (host={RABBITMQ_HOST})...")
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        heartbeat=15,
        blocked_connection_timeout=10,
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[*] Connected to RabbitMQ! Waiting for messages in queue '{QUEUE_NAME}'.")
    channel.start_consuming()


if __name__ == '__main__':
    while True:
        try:
            connect_and_consume()
        except KeyboardInterrupt:
            print("\n[*] Stopping PDF worker...")
            break
        except Exception as e:
            print(f"[!] Worker connection cycle exhausted: {e}. Restarting retry cycle in 5s...")
            time.sleep(5)
