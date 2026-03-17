# SkySecure Airlines 
System zakupu i rezerwacji biletów lotniczych dla linii pasażerskich "SkySecure Airlines".

## Status projektu: Sprint 2 (Zakończony)

W tym sprincie przenieśliśmy architekturę na poziom produkcyjny, wprowadzając konteneryzację, profesjonalną bazę danych oraz system bezpieczeństwa.

### Co zostało zrobione (Sprint 2):

#### 1. Konteneryzacja i Infrastruktura (DevOps)
* **Docker & Docker Compose**: Cały system został podzielony na 3 współpracujące usługi: `backend`, `db` (PostgreSQL) oraz `proxy` (Nginx).
* **Nginx Reverse Proxy**: Skonfigurowano serwer proxy, który obsługuje ruch na porcie 80 i przekierowuje zapytania `/api/` do backendu.
* **PostgreSQL**: Migracja z SQLite na pełnoprawną bazę danych PostgreSQL 15.

#### 2. Bezpieczeństwo i Autentykacja
* **Rejestracja i Logowanie**: Implementacja pełnego przepływu użytkownika (Register/Login).
* **Hashing haseł**: Wykorzystanie nowoczesnego algorytmu **Argon2** do bezpiecznego przechowywania haseł w bazie.
* **JWT (JSON Web Tokens)**: System generowania tokenów dostępu dla zalogowanych użytkowników.

#### 3. Udoskonalenia Backend (FastAPI)
* **Refaktoryzacja main.py**: Poprawa kolejności inicjalizacji aplikacji i routerów.
* **Pydantic Schemas**: Stworzenie modeli walidacji danych dla użytkowników i tokenów.
* **Healthcheck 2.0**: Endpoint weryfikujący połączenie z bazą PostgreSQL przez Nginx.

---

## 🛠 Technologia
* **Framework**: FastAPI
* **Baza danych**: PostgreSQL 15 + SQLAlchemy (ORM)
* **Serwer Proxy**: Nginx
* **Kontenery**: Docker + Docker Compose
* **Bezpieczeństwo**: Passlib (Argon2), PyJWT

---

## Jak uruchomić projekt (Docker)

To najprostszy sposób. Nie musisz niczego instalować lokalnie (oprócz Dockera).

1. **Sklonuj repozytorium:**
   ```bash
   git clone [https://github.com/DidiGaga-cyber/skysecure-airlines.git](https://github.com/DidiGaga-cyber/skysecure-airlines.git)
   cd skysecure-airlines
