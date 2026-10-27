# SkySecure Airlines

> Zaawansowany i bezpieczny system zakupu oraz rezerwacji biletów lotniczych dla linii pasażerskich **SkySecure Airlines**, zrealizowany w architekturze mikroserwisowej / SOA z asynchronicznym przetwarzaniem zadań i ochroną klasy OWASP.

---

## Spis treści
- [Opis projektu](#opis-projektu)
- [Architektura systemu](#architektura-systemu)
- [Stos technologiczny](#stos-technologiczny)
- [Główne funkcjonalności](#główne-funkcjonalności)
- [Model danych i baza relacyjna](#model-danych-i-baza-relacyjna)
- [Bezpieczeństwo i mechanizmy ochrony](#bezpieczeństwo-i-mechanizmy-ochrony)
- [Import i migracja danych (ETL)](#import-i-migracja-danych-etl)
- [Struktura repozytorium](#struktura-repozytorium)
- [Specyfikacja API (REST)](#specyfikacja-api-rest)
- [Instrukcja uruchomienia](#instrukcja-uruchomienia)
- [Konta testowe](#konta-testowe)
- [Testy integracyjne](#testy-integracyjne)
- [Autorzy](#autorzy)
- [Zrzuty ekranu](#zrzuty-ekranu)

---

## Opis projektu

**SkySecure Airlines** to kompleksowa aplikacja webowa do obsługi rezerwacji i zakupu biletów lotniczych online. System zapewnia pasażerom wyszukiwanie połączeń w czasie rzeczywistym, interaktywną mapę miejsc w samolocie, moduł płatności oraz automatyczne, asynchroniczne generowanie e-biletów PDF z wykorzystaniem kolejki komunikatów.

Dla zarządców siatki połączeń przygotowano dedykowany panel administracyjny umożliwiający zarządzanie lotami, kontrolę statusów operacyjnych (`Zaplanowany`, `Opóźniony`, `W trakcie`, `Zakończony`, `Odwołany`) oraz wgląd w rejestr zdarzeń audytowych.

---

## Architektura systemu

Aplikacja oparta jest na nowoczesnej architekturze **zorientowanej na usługi (SOA) / mikroserwisowej** ze skalowalnym klastrem kontenerów Docker Compose:

1. **Klient (SPA):** Interaktywny frontend napisany w Vue 3 i ostylowany w Tailwind CSS.
2. **Brama brzegowa / Reverse Proxy / WAF:** Serwer Nginx zintegrowany z modułem **OWASP ModSecurity Core Rule Set (CRS)**, zapewniający terminację TLS/SSL, ochronę przed atakami webowymi, buforowanie i load balancing backendu.
3. **Usługa API (Backend):** Zduplikowane instancje FastAPI (`backend-1` i `backend-2`), realizujące logikę biznesową, autoryzację OAuth2/JWT oraz kontrolę dostępu opartą na rolach (RBAC).
4. **Broker komunikatów:** **RabbitMQ** z trwałymi kolejkami (`ticket_pdf_queue`) oraz gwarancją dostarczenia wiadomości (`delivery_mode=2`).
5. **Mikroserwis generowania dokumentów (Worker):** Dedykowana usługa konsumencka `PdfService` (`pdf_worker`), przetwarzająca zadania w tle zaimplementowana ze wzorcem ponawiania prób (**Retry Pattern** z opóźnieniem wykładniczym).
6. **Baza danych:** Relacyjna baza **PostgreSQL 15** z funkcjami kryptograficznymi `pgcrypto`, mechanizmami blokowania pesymistycznego (concurrency control) oraz automatycznymi wyzwalaczami generowania miejsc.

```
       [ Użytkownik / Przeglądarka ]
                    │
                    ▼  HTTPS (443)
       ┌───────────────────────────────┐
       │   Nginx Reverse Proxy + WAF   │
       │   (OWASP ModSecurity CRS)     │
       └───────┬───────────────┬───────┘
               │               │
  /api/ (Load Balancing)       │ / (Static Files)
       ┌───────┴───────┐       ▼
       ▼               ▼   [ Frontend SPA (Vue 3) ]
 [ Backend Replika 1 ] [ Backend Replika 2 ]
       │               │
       ├───────────────┴────────────────────────┐
       ▼                                        ▼
[ PostgreSQL 15 ] (SQLAlchemy / ACID)     [ RabbitMQ Broker ]
                                                │
                                                ▼ (AMQP Task Queue)
                                         [ PdfService Worker ]
                                                │
                                                ▼
                                         [ Katalog PDF ]
```

---

## Stos technologiczny

| Warstwa | Technologie |
|---|---|
| **Frontend** | Vue 3 (Composition API), Tailwind CSS, Axios, Google Material Icons |
| **Backend API** | Python 3.11, FastAPI, Pydantic, SQLAlchemy 2.0, Jose (JWT), Tenacity |
| **Kolejkowanie & SOA** | RabbitMQ 3 (Management), Pika (AMQP Client), FPDF2 |
| **Baza danych** | PostgreSQL 15, `pgcrypto` (AES-256), PL/pgSQL Triggers |
| **Bezpieczeństwo** | ModSecurity WAF, OWASP CRS, Argon2id, OAuth2 Bearer Tokens, RBAC |
| **Infrastruktura** | Docker, Docker Compose, Nginx (Alpine), Multi-stage Dockerfiles |

---

## Główne funkcjonalności

### Dla Pasażerów:
- **Wyszukiwarka połączeń:** Filtrowanie lotów według lotniska wylotu, przylotu i daty podróży.
- **Weryfikacja statusu:** Blokada rezerwacji na loty o statusie innym niż `Zaplanowany` (np. loty opóźnione, odwołane lub zrealizowane).
- **Interaktywna mapa pokładu:** Wybór konkretnego miejsca w klasie Economy lub Business z dynamicznym podglądem zajętości.
- **Wielokanałowe płatności:** Symulacja płatności kartą debetową/kredytową, kodem BLIK lub Apple Pay z szyfrowaniem identyfikatorów transakcji.
- **Pobieranie e-biletu PDF:** Błyskawiczny dostęp do wygenerowanego w tle dokumentu podróżnego z unikalnym identyfikatorem rezerwacji.
- **Panel pasażera:** Przegląd historii rezerwacji, statusów opłat oraz pobieranie archiwalnych biletów.

### Dla Administratorów:
- **Panel zarządzania lotami (Dark Mode):** Dodawanie nowych połączeń z automatyczną generacją miejsc pokładowych.
- **Edycja i anulowanie połączeń:** Modyfikacja parametrów lotu, cen oraz stanów operacyjnych (`Zaplanowany`, `Opóźniony`, `W trakcie`, `Zakończony`, `Odwołany`).
- **Nadzór bazy i miejsc:** Kaskadowe usuwanie powiązań z poszanowaniem integralności biletów opłaconych.
- **Dostęp RBAC:** Rygorystyczna separacja uprawnień administracyjnych od zwykłych użytkowników na poziomie aplikacji i bazy danych.

---

## Model danych i baza relacyjna

Baza danych operuje na spójnym schemacie relacyjnym z kluczami obcymi i indeksami wydajnościowymi:

1. **`uzytkownicy`** — Identyfikatory, imię, nazwisko, unikalny email, hasło (hash Argon2id), rola w systemie (`User`, `Admin`).
2. **`lotniska`** — Kod IATA (unikalny klucz biznesowy, np. WAW, JFK), pełna nazwa, miasto, kraj.
3. **`loty`** — Relacje z lotniskiem wylotu i przylotu, czasy odlotu/przylotu, cena bazowa, liczba miejsc, status operacyjny.
4. **`miejsca`** — Fizyczny układ pokładu dla każdego lotu, oznaczenie rzędu i fotela (np. 1A, 12F), klasa (`Economy`, `Business`), flaga `czy_wolne`.
5. **`rezerwacje`** — Zamówienie powiązane z użytkownikiem i lotem, kwota łączna, status (`Oczekująca`, `Opłacona`, `Anulowana`).
6. **`bilety`** — Przypisanie pasażera do rezerwacji oraz konkretnego miejsca w samolocie.
7. **`platnosci`** — Ewidencja transakcji powiązana z rezerwacją, metoda, kwota, status oraz identyfikator sesji UUID.
8. **`logi_audytowe`** — Dziennik bezpieczeństwa rejestrujący kluczowe akcje systemu, adresy IP, identyfikatory użytkowników i znaczniki czasu.

---

## Bezpieczeństwo i mechanizmy ochrony

- **Zapora WAF (ModSecurity + OWASP Core Rule Set):** Wykrywanie i blokowanie ataków SQL Injection, XSS, Path Traversal, HTTP Request Smuggling oraz złośliwych botów.
- **Uwierzytelnianie & Autoryzacja:** Standard OAuth2 Password Bearer z podpisem HMAC-SHA256 (JWT), mechanizm wygasania tokenów i obsługa bezpiecznego wylogowania.
- **Haszowanie haseł:** Nowoczesny algorytm **Argon2id** (odporny na ataki GPU/ASIC i brute-force).
- **Poziom bazy danych (PostgreSQL RBAC):** Ustawianie ról sesyjnych w bazie (`SET LOCAL ROLE app_admin_role` / `app_user_role`) zależnie od tożsamości z tokena.
- **Ochrona przed wyścigami (Race Conditions):** Blokowanie pesymistyczne wiersza bazy (`with_for_update()`) podczas rezerwacji miejsc.
- **Audyt OWASP:** Szczegółowe logowanie zdarzeń autoryzacyjnych, płatniczych i administracyjnych w tabeli audytu.

---

## Import i migracja danych (ETL)

W projekcie zaimplementowano skrypt **[`BackEnd/import_data.py`](BackEnd/import_data.py)** realizujący jednostronny transfer danych z plików CSV do relacyjnej bazy PostgreSQL:

- Obsługiwane pliki źródłowe: `lotniska.csv`, `uzytkownicy.csv`, `loty.csv`.
- Walidacja typów danych, normalizacja dat ISO/Timestamp oraz czyszczenie wartości pustych (`NaN`).
- Obsługa integralności relacji kluczy obcych (`ensure_airport_exists`).
- Idempotentność i odporność na duplikaty (`ON CONFLICT DO NOTHING`).
- Skrypt wykonuje się automatycznie przy starcie kontenera backendowego oraz może być uruchamiany niezależnie.

---

## Struktura repozytorium

```
skysecure-airlines/
│
├── BackEnd/                    # Aplikacja FastAPI (REST API)
│   ├── tests/                  # Testy integracyjne (pytest)
│   │   └── test_integration.py
│   ├── auth.py                 # Endpointy rejestracji, logowania i middleware JWT
│   ├── auth_utils.py           # Narzędzia kryptograficzne (Argon2id, tokeny JWT)
│   ├── bookings.py             # Logika rezerwacji miejsc i transakcji
│   ├── database.py             # Konfiguracja SQLAlchemy i sesji bazy danych
│   ├── flights.py              # Wyszukiwanie, pobieranie i edycja lotów
│   ├── import_data.py          # Skrypt ETL importujący dane z CSV
│   ├── main.py                 # Punkt wejścia aplikacji FastAPI
│   ├── models.py               # Modele relacyjne ORM
│   ├── payments.py             # Obsługa transakcji płatniczych
│   ├── schemas.py              # Schematy walidacji Pydantic
│   ├── tickets.py              # Wystawianie biletów i publikacja zadań do RabbitMQ
│   ├── lotniska.csv            # Dane źródłowe: lotniska
│   ├── loty.csv                # Dane źródłowe: loty
│   ├── uzytkownicy.csv         # Dane źródłowe: użytkownicy
│   └── Dockerfile
│
├── FrontEnd/                   # Interfejs użytkownika SPA (HTML5 / Vue 3)
│   ├── js/                     # Logika modułów Vue i komunikacji Axios
│   │   ├── admin.js            # Obsługa panelu administratora
│   │   ├── index.js            # Wyszukiwarka, mapa miejsc i płatności
│   │   ├── login.js            # Logowanie i rejestracja
│   │   ├── notify.js           # Powiadomienia toast i modale
│   │   ├── profile.js          # Widok profilu i pobieranie biletów
│   │   └── state.js            # Globalny stan sesji i interceptory JWT
│   ├── admin.html              # Panel administratora (Dark Mode)
│   ├── index.html              # Strona główna z wyszukiwarką i rezerwacją
│   ├── login.html              # Formularze autoryzacji
│   └── profile.html            # Panel użytkownika
│
├── PdfService/                 # Mikroserwis SOA generowania dokumentów PDF
│   ├── pdf_worker.py           # Konsument kolejki RabbitMQ z Retry Pattern
│   ├── requirements.txt
│   └── Dockerfile
│
├── DataBase/                   # Skrypty inicjalizujące PostgreSQL
│   ├── 01_schema.sql           # DDL tabel, indeksy i wyzwalacze miejsc
│   ├── 02_seed.sql             # Dane testowe (użytkownicy, loty, rezerwacje)
│   └── 03_roles_and_permissions.sql # Uprawnienia ról SQL
│
├── Nginx/                      # Konfiguracja reverse proxy i certyfikaty SSL
│   ├── certs/                  # Certyfikaty SSL/TLS
│   └── nginx.conf              # Konfiguracja Nginx, SSL, WAF oraz upstreamów API
│
├── generated_pdfs/             # Współdzielony wolumen wygenerowanych biletów PDF
├── docker-compose.yml          # Konfiguracja klastra wielokontenerowego
└── README.md                   # Dokumentacja projektu
```

---

## Specyfikacja API (REST)

Dokumentacja interaktywna Swagger UI jest dostępna pod adresem: `https://localhost/api/docs`

| Metoda | Endpoint | Wymagane uprawnienia | Opis |
|---|---|---|---|
| `POST` | `/api/auth/register` | Publiczny | Rejestracja nowego pasażera |
| `POST` | `/api/auth/login` | Publiczny | Logowanie (OAuth2 form), zwrot tokenu JWT |
| `GET` | `/api/health` | Publiczny | Healthcheck dostępności API i bazy |
| `GET` | `/api/flights/` | Publiczny | Wyszukiwanie lotów (filtry: `from`, `to`, `date`) |
| `GET` | `/api/flights/{id}/seats` | Publiczny | Pobranie mapy i dostępności miejsc w locie |
| `GET` | `/api/flights/airports/{id}` | Publiczny | Pobranie szczegółów lotniska po ID |
| `POST` | `/api/flights/` | **Admin** | Utworzenie nowego lotu i generowanie miejsc |
| `PUT` | `/api/flights/{id}` | **Admin** | Aktualizacja parametrów lub statusu lotu |
| `DELETE`| `/api/flights/{id}` | **Admin** | Usunięcie lotu z bazy |
| `POST` | `/api/bookings/` | Zalogowany (**User/Admin**) | Utworzenie rezerwacji wstępnej |
| `POST` | `/api/tickets/` | Zalogowany (**User/Admin**) | Przypisanie pasażera do miejsca i wysłanie zadania PDF do RabbitMQ |
| `GET` | `/api/tickets/{id}/pdf` | Zalogowany (**User/Admin**) | Pobranie gotowego pliku e-biletu PDF |
| `POST` | `/api/payments/process` | Zalogowany (**User/Admin**) | Przetworzenie płatności za rezerwację |

---

## Instrukcja uruchomienia

### Wymagania wstępne
- **Docker Desktop** (uruchomiony silnik Docker)
- Nowoczesna przeglądarka internetowa (Chrome, Edge, Firefox)

### 1. Pobranie repozytorium
```bash
git clone https://github.com/DidiGaga-cyber/skysecure-airlines.git
cd skysecure-airlines
```

### 2. Konfiguracja zmiennych środowiskowych (.env)
Utwórz plik `.env` w głównym katalogu projektu:
```env
DATABASE_URL=postgresql://skysecure_user:skysecure_password@db:5432/skysecure_db
DB_ENCRYPTION_KEY=skysecure_super_secret_encryption_key_2026!
SECRET_KEY=super_secret_jwt_key_skysecure_production_token_signature_2026
```

### 3. Uruchomienie klastra
```bash
docker-compose down -v
docker-compose up -d --build
```
> **Uwaga:** Flaga `-v` czyści stare wolumeny bazodanowe, zapewniając wykonanie świeżej migracji schematu i załadowanie danych początkowych.

### 4. Dostęp do usług
- **Aplikacja kliencka:** [https://localhost](https://localhost)
- **Dokumentacja API (Swagger):** [https://localhost/api/docs](https://localhost/api/docs)
- **Panel zarządzania RabbitMQ:** [http://localhost:15672](http://localhost:15672) (użytkownik: `guest`, hasło: `guest`)

---

## Konta testowe

Do weryfikacji działania systemu można skorzystać z predefiniowanych kont:

| Rola | Adres Email | Hasło | Zastosowanie |
|---|---|---|---|
| **Administrator** | `admin@skysecure.pl` | `SuperSecretPassword123` | Zarządzanie lotami w panelu admina (`admin.html`) |
| **Pasażer testowy** | `test@skysecure.pl` | `SuperSecretPassword123` | Wyszukiwanie, rezerwacja, płatności i pobieranie biletów |

---

## Testy integracyjne

W kontenerze backendu przygotowano zestaw testów integracyjnych weryfikujących sprawność brokera RabbitMQ oraz pełny cykl End-to-End generowania dokumentów PDF:

```bash
docker exec -it skysecure_backend_1 pytest tests/test_integration.py -v
```

Testy weryfikują:
1. Prawidłowe nawiązanie łączności z kolejką RabbitMQ.
2. Nadanie zadania generowania biletu do kolejki `ticket_pdf_queue`.
3. Wygenerowanie pliku PDF przez konsumenta `pdf_worker`.
4. Poprawność pobrania pliku PDF przez endpoint REST API.

---

## Autorzy

| Członek Zespołu | Zakres odpowiedzialności |
|---|---|
| **Valentyn** | Architektura bazy danych, infrastruktura Docker, RabbitMQ, bezpieczeństwo WAF |
| **Dmitrii H.** | Logika biznesowa backendu (FastAPI), integracja brokera, transakcje |
| **Dmytro D.** | Interfejs użytkownika (Vue 3, Tailwind), mapa pokładu, responsywność |

---

## Zrzuty ekranu

<!-- Strona główna z wyszukiwarką lotów -->
<img width="1919" height="1060" alt="Strona główna" src="https://github.com/user-attachments/assets/ea9f3bfb-1f27-4de8-a84d-84ef1e130311" />
*(Wyszukiwarka lotów na stronie głównej)*

<!-- Interaktywna mapa miejsc -->
<img width="1898" height="1053" alt="Mapa miejsc" src="https://github.com/user-attachments/assets/9b926aad-0630-4121-a093-edf552fd6d0f" />
*(Interaktywna mapa pokładu samolotu)*

<!-- Finalizacja i sukces -->
<img width="1895" height="1051" alt="Formularz płatności" src="https://github.com/user-attachments/assets/c5735c32-12a2-4043-a52a-095a20f06df7" />
*(Formularz płatności i bezpieczeństwo transakcji)*

<img width="1919" height="1045" alt="Potwierdzenie" src="https://github.com/user-attachments/assets/b0c0a5ce-f824-4f25-a057-4466729e5652" />
*(Ekran potwierdzenia rezerwacji z opcją pobrania PDF)*

<!-- E-bilet PDF -->
<img width="785" height="493" alt="Wygenerowany bilet PDF" src="https://github.com/user-attachments/assets/7a9ad4ee-eaa4-43ee-b92f-55e5d3d33b27" />
*(Wygenerowany bilet PDF z kolejki RabbitMQ)*

<!-- Panel Administratora -->
<img width="1915" height="1058" alt="Panel Administratora" src="https://github.com/user-attachments/assets/85ae31dd-2d79-4daf-9291-d8c771ce4eb9" />
*(Panel Administratora w Dark Mode)*
