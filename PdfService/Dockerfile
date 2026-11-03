FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_worker.py .

# Unbuffered stdout for immediate Docker log output
CMD ["python", "-u", "pdf_worker.py"]
