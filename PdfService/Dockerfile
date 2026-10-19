FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_worker.py .

# Запуск с флагом -u для мгновенного вывода логов в консоль Docker
CMD ["python", "-u", "pdf_worker.py"]