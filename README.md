# SkySecure Airlines

> System zakupu i rezerwacji biletów lotniczych dla linii pasażerskich **SkySecure Airlines**.

## Opis projektu

**SkySecure Airlines** to webowa aplikacja do zakupu i rezerwacji biletów lotniczych, stworzona z myślą o pasażerach poszukujących szybkiego i bezpiecznego systemu rezerwacji online. Aplikacja umożliwia wyszukiwanie lotów, wybór miejsc, płatność oraz pobranie e-biletu w formacie PDF.

**Cel:** Zapewnienie w pełni funkcjonalnego, bezpiecznego systemu rezerwacji lotów z panelem administracyjnym oraz ochroną przed podstawowymi atakami OWASP.

**Grupa docelowa:** Pasażerowie linii SkySecure Airlines oraz administratorzy systemu zarządzający siatką połączeń.

---

## Status projektu: Sprint 7 — UKOŃCZONY

---

## Co zostało zrobione

### Sprint 1 — Szkielet projektu
> Szkielet projektu uruchamia się lokalnie u każdego członka zespołu bez błędów.

* **Setup ClickUp & GitHub** — Założenie repozytorium na GitHub z dostępami, konfiguracja tablicy w ClickUp.
* **Docker: Pusta Baza** — Plik `docker-compose.yml` podnoszący instancję PostgreSQL.
* **Setup FastAPI & SQLAlchemy** — Konfiguracja pustego projektu API i połączenia z bazą danych.
* **Endpoint Healthcheck** — Endpoint `/api/health` do weryfikacji działania serwera.
* **Setup Vue 3 & Tailwind CSS** — Utworzenie projektu SPA i konfiguracja bazowych stylów.
* **Puste widoki (Routing)** — Vue Router z pustymi stronami (Home, Login).

---

### Sprint 2 — Autoryzacja użytkowników
> Użytkownik może otworzyć stronę, założyć konto i zalogować się do systemu.

* **SQL DDL: Użytkownicy** — Skrypt tworzący tabelę `Użytkownicy`.
* **Reverse Proxy (Nginx)** — Nginx w Dockerze kierujący ruch na FastAPI (port 80 → 8000).
* **Logowanie i Rejestracja** — Endpointy autoryzacji z hashowaniem Argon2 i JWT (UC-1, UC-12).
* **Model User (ORM)** — Model użytkownika w SQLAlchemy.
* **Widok: Formularze Auth** — Ekrany logowania/rejestracji z walidacją danych.
* **Zapis Tokenu JWT** — Logika Vue do przechowywania sesji użytkownika w `localStorage`.

---

### Sprint 3 — Wyszukiwarka lotów
> System wyświetla dostępne loty na stronie głównej i pozwala na ich wyszukiwanie.

* **SQL DDL: Loty i Lotniska** — Tabele `Loty`, `Samoloty`, `Lotniska` z relacjami.
* **Seeding: Dane testowe** — Skrypt SQL z fikcyjnymi lotniskami i lotami (m.in. WAW-JFK, LUZ-LHR).
* **Wyszukiwarka (API)** — Endpoint `GET /flights` filtrujący loty po dacie i trasie (UC-2).
* **Widok: Strona Główna** — Hero Section z wyszukiwarką.
* **Integracja Wyników** — Wyświetlanie wyników z bazy w formie tabeli (czas, cena).

---

### Sprint 4 — Wybór miejsc i rezerwacja
> Pasażer może wybrać konkretne miejsce w samolocie z interaktywnej mapy.

* **SQL DDL: Rezerwacje i Miejsca** — Tabele `Rezerwacje`, `Bilety`, `Miejsca`.
* **Mapa miejsc (API)** — Endpoint zwracający aktualny stan miejsc dla lotu (wolne/zajęte).
* **Tworzenie Rezerwacji** — Logika tworzenia wstępnej rezerwacji „Oczekującej" (UC-3).
* **Interaktywna Mapa Miejsc** — Mapa samolotu z legendą kolorystyczną (UC-7).
* **Formularz Pasażerów** — Ekran wprowadzania danych personalnych do biletu.

---

### Sprint 5 — Płatności
> Użytkownik może sfinalizować zamówienie i uzyskać potwierdzenie płatności.

* **SQL DDL: Płatności** — Tabela `Płatności` powiązana z `Rezerwacjami`.
* **Szyfrowanie AES-256** — Konfiguracja `pgcrypto` do szyfrowania danych paszportowych.
* **Mock Bramki Płatniczej** — Endpoint symulujący autoryzację płatności (UC-5).
* **Widok Płatności** — Ekran wprowadzania danych karty z elementami wizualnego bezpieczeństwa.
* **Ekran Sukcesu** — Widok z podsumowaniem zakupu.

---

### Sprint 6 — Panel Administratora
> Administrator posiada ukryty panel do zarządzania siatką połączeń i statystykami.

* **SQL: Role i Uprawnienia** — Weryfikacja struktury i dostępów dla roli `Admin` na poziomie bazy.
* **Zarządzanie Lotami (API)** — Endpointy CRUD (Dodaj, Usuń) z wymogiem tokena Admina (UC-9).
* **Generowanie PDF (E-ticket)** — Logika generowania biletu w formacie PDF (UC-6).
* **Panel Admina (Dark Mode)** — Osobny routing do panelu z odmienną kolorystyką.
* **Tabela Lotów (Frontend)** — Główny widok do zarządzania i dodawania nowych lotów.

---

### Sprint 7 — Bezpieczeństwo i gotowość do obrony
> Aplikacja jest zabezpieczona przed podstawowymi atakami (OWASP) i gotowa do obrony projektu.

* **Wdrożenie WAF & SSL/TLS** — Konfiguracja ModSecurity i certyfikatów HTTPS.
* **Rate Limiting & Logi** — Ochrona przed Brute Force oraz logi audytowe operacji bazy.
* **Bugfixing API** — Analiza i poprawki błędów według testów Postman.
* **Wygasanie sesji JWT** — Frontendowa logika wylogowania po wygaśnięciu tokenu.
* **Odprawa Online (UI)** — Zakładka „Moje loty" z opcją pobrania biletu PDF i odprawy (UC-8).

---

## Demo i zrzuty ekranu

<!-- 📸 SCREENSHOT: Strona główna z wyszukiwarką lotów (Hero Section) -->
<img width="1919" height="1060" alt="image" src="https://github.com/user-attachments/assets/ea9f3bfb-1f27-4de8-a84d-84ef1e130311" />

> *(Zrzut ekranu strony głównej z wyszukiwarką)*

<!-- 📸 SCREENSHOT: Interaktywna mapa miejsc w samolocie -->
<img width="1898" height="1053" alt="image" src="https://github.com/user-attachments/assets/9b926aad-0630-4121-a093-edf552fd6d0f" />

> *(Zrzut ekranu mapy miejsc z legendą kolorystyczną)*

<!-- 📸 SCREENSHOT: Ekran płatności i ekran sukcesu -->
<img width="1895" height="1051" alt="image" src="https://github.com/user-attachments/assets/c5735c32-12a2-4043-a52a-095a20f06df7" />
<img width="1917" height="1012" alt="image" src="https://github.com/user-attachments/assets/10e26ad0-d215-4129-927f-0ee6fbe88482" />


> *(Zrzut ekranu formularza płatności i potwierdzenia zakupu)*

<!-- 📸 SCREENSHOT: Panel Administratora (Dark Mode) -->
<img width="1915" height="1058" alt="image" src="https://github.com/user-attachments/assets/85ae31dd-2d79-4daf-9291-d8c771ce4eb9" />

> *(Zrzut ekranu panelu admina w trybie ciemnym)*

---

## Technologia

| Warstwa | Technologie |
|---|---|
| **Frontend** | Vue 3, Tailwind CSS, Axios |
| **Backend** | FastAPI, PyJWT, Passlib (Argon2) |
| **Baza danych** | PostgreSQL 15, SQLAlchemy (ORM), pgcrypto (AES-256) |
| **Bezpieczeństwo** | ModSecurity (WAF), SSL/TLS, Rate Limiting, JWT |
| **Infrastruktura** | Nginx, Docker, Docker Compose |

---

## Struktura bazy danych

System operuje na 6 powiązanych relacyjnie tabelach:

1. **Użytkownicy** — dane osobowe, hasło (Argon2), rola (pasażer / admin)
2. **Lotniska** — kod IATA (np. WAW, LUZ), nazwa, miasto, kraj
3. **Loty** — numer lotu, klucze obce do lotnisk (odlot/przylot), czasy, cena, liczba miejsc
4. **Miejsca** — stan miejsca (wolne/zajęte), powiązanie z lotem
5. **Rezerwacje** — status rezerwacji, powiązanie z użytkownikiem i lotem
6. **Płatności** — dane transakcji, powiązanie z rezerwacją (dane paszportowe szyfrowane AES-256)

---

## Jak uruchomić projekt

### Wymagania
- Docker Desktop (uruchomiony)
- Przeglądarka internetowa

### Krok 1: Pobranie kodu

```bash
git clone https://github.com/DidiGaga-cyber/skysecure-airlines.git
cd skysecure-airlines
```

### Krok 2: Pobranie .env

Utwórz file .env i wstaw secret kłuche które otrzymał od członka zespołu
```bash
DATABASE_URL=****
DB_ENCRYPTION_KEY=****
```

### Krok 3: Uruchomienie infrastruktury

```bash
docker-compose down -v
docker-compose up -d --build
```

> Flaga `-v` jest wymagana do wyczyszczenia starych wolumenów i załadowania nowych danych testowych.

### Krok 4: Weryfikacja API

Poczekaj 10–15 sekund na inicjalizację bazy, następnie otwórz dokumentację Swagger:

```
https://localhost/api/docs
```

<!-- 📸 SCREENSHOT: Widok Swagger UI z listą endpointów API -->
<img width="1887" height="1046" alt="image" src="https://github.com/user-attachments/assets/249f11d1-f513-4955-97d5-52894563fac5" />

> *(Zrzut ekranu interfejsu Swagger /api/docs)*

### Krok 5: Uruchomienie aplikacji klienckiej

Otwórz folder `FrontEnd` i kliknij dwukrotnie plik `main.html` (otworzy się w przeglądarce).

### Krok 6: Logowanie testowe

Możesz zarejestrować nowego użytkownika lub skorzystać z gotowych kont:

| Rola | Email | Hasło |
|---|---|---|
| Administrator | `admin@skysecure.pl` | `SuperSecretPassword123` |
| Pasażer testowy | `test@skysecure.pl` | `SuperSecretPassword123` |

---

## Zespół

| Członek | Odpowiedzialność |
|---|---|
| **Valentyn** | DevOps, baza danych, infrastruktura, bezpieczeństwo |
| **Dmitrii H.** | Backend (FastAPI), logika biznesowa, API |
| **Dmytro D.** | Frontend (Vue 3), interfejs użytkownika |
