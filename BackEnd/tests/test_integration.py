import os
import time
import json
import requests
import pika
import pytest

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "ticket_pdf_queue"
PDF_DIR = "/app/pdfs"

def test_rabbitmq_connection():
    """1. Тест доступности брокера сообщений RabbitMQ"""
    try:
        # Используем socket_timeout вместо timeout
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, socket_timeout=5)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        connection.close()
        assert True
    except Exception as e:
        pytest.fail(f"Nie udało się połączyć z RabbitMQ: {e}")

def test_pdf_generation_e2e():
    """
    2. End-to-End тест интеграции:
       - Отправка тестовой задачи в RabbitMQ
       - Проверка генерации PDF-файла сервисом pdf_worker
       - Получение готового PDF через API
    """
    test_ticket_id = 9999
    payload = {
        "ticket_id": test_ticket_id,
        "passenger_name": "Test Integration User",
        "flight_number": "LO-500",
        "seat": "12A"
    }

    # Отправляем валидный JSON напрямую в RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

    # Ждем до 7 секунд, пока pdf_worker вычитает очередь и создаст файл
    expected_file = os.path.join(PDF_DIR, f"ticket_{test_ticket_id}.pdf")
    file_created = False
    
    for _ in range(14):
        if os.path.exists(expected_file):
            file_created = True
            break
        time.sleep(0.5)

    assert file_created, f"Plik {expected_file} nie został wygenerowany przez pdf_worker!"

    # Проверяем отдачу файла через API
    response = requests.get(f"{BASE_URL}/tickets/{test_ticket_id}/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0

    # Очистка созданного во время теста файла
    if os.path.exists(expected_file):
        os.remove(expected_file)