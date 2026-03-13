# skysecure-airlines
System zakupu i rezerwacji biletów lotniczych dla linii pasażerskich "SkySecure Airlines".


# SkySecure Airlines - Backend

System rezerwacji i zakupu biletów lotniczych. Ta część repozytorium zawiera logikę serwerową (API) oraz konfigurację bazy danych.

## Co zostało zrobione (Sprint 1):

### 1. Konfiguracja projektu (Setup)
* Inicjalizacja środowiska wirtualnego (`venv`).
* Konfiguracja pliku `.gitignore` w celu wykluczenia plików tymczasowych i bazy danych z repozytorium.
* Przygotowanie pliku `requirements.txt` z listą niezbędnych bibliotek.

### 2. Wybór i instalacja technologii
* **FastAPI**: Wykorzystany jako nowoczesny i wydajny framework do budowy API.
* **SQLAlchemy**: Konfiguracja ORM do komunikacji z bazą danych.
* **Uvicorn**: Serwer ASGI do uruchamiania aplikacji.

### 3. Architektura bazy danych
* Stworzenie modułu `database.py`.
* Konfiguracja połączenia z bazą danych (SQLite w fazie deweloperskiej).
* Inicjalizacja `SessionLocal` oraz klasy bazowej `Base` dla przyszłych modeli.

### 4. Implementacja Endpointów
* Stworzenie głównej aplikacji FastAPI w pliku `main.py`.
* Dodanie endpointu testowego **Healthcheck** (`/health`), który pozwala zweryfikować poprawność działania serwera oraz połączenia z bazą danych.

## Jak uruchomić projekt lokalnie:

1. Aktywuj środowisko wirtualne: `venv\Scripts\activate`
2. Zainstaluj biblioteki: `pip install -r requirements.txt`
3. Uruchom serwer: `python -m uvicorn main:app --reload`
4. Dokumentacja Swagger UI dostępna pod adresem: `http://127.0.0.1:8000/docs`
