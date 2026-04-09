# SkySecure Airlines 
System zakupu i rezerwacji biletów lotniczych dla linii pasażerskich "SkySecure Airlines".

## Status projektu: Sprint 3 (W trakcie)
W tym sprincie skupiamy sie na integracji systemow oraz rozbudowie logiki biznesowej dla lotow i lotnisk.

### Co zostalo zrobione (Sprint 3):
#### 1. Integracja Frontend & Backend
* **Axios**: Wdrozenie biblioteki po stronie klienta (Vue 3).
* **Pelny cykl autoryzacji**: Rejestracja i logowanie bezposrednio z poziomu interfejsu (HTML/JS) do bazy danych PostgreSQL poprzez proxy Nginx.
* **Zarzadzanie sesja**: Bezpieczne przechowywanie prawdziwych tokenow JWT w localStorage.
* **Naprawa routingu**: Optymalizacja prefiksow API (/auth) dla bezproblemowej wspolpracy FastAPI z Nginx.

#### 2. Rozbudowa Bazy Danych (DevOps & DBA)
* **Migracje i Seeding**: Podzial inicjalizacji bazy na profesjonalne skrypty: 01_schema.sql (struktura) i 02_seed.sql (dane testowe).
* **Nowe Encje**: Dodanie relacyjnych tabel Lotniska (Slownik lotnisk IATA) oraz Loty (Polaczenia lotnicze).
* **Dane Testowe**: Automatyczne tworzenie konta administratora, testowego pasazera oraz przykladowych tras lotniczych (m.in. WAW-JFK, LUZ-LHR).

### Co zostalo zrobione (Sprint 2):
* Konteneryzacja (Docker, Docker Compose).
* Nginx Reverse Proxy (port 80 -> backend:8000).
* Migracja na PostgreSQL 15.
* Hashing hasel Argon2 i system JWT.

---

## Technologia
* **Frontend**: Vue 3, Tailwind CSS, Axios
* **Backend**: FastAPI, PyJWT, Passlib (Argon2)
* **Baza danych**: PostgreSQL 15 + SQLAlchemy (ORM)
* **Infrastruktura**: Nginx, Docker + Docker Compose

---

## Jak uruchomic projekt krok po kroku

System sklada sie z infrastruktury backendowej (Docker) oraz klienta frontendowego (przegladarka).

### Krok 1: Pobranie kodu
```bash
git clone [https://github.com/DidiGaga-cyber/skysecure-airlines.git](https://github.com/DidiGaga-cyber/skysecure-airlines.git)
cd skysecure-airlines
```

### Krok 2: Uruchomienie infrastruktury (Baza + Serwery)
Upewnij sie, ze Docker jest wlaczony, a nastepnie w terminalu wykonaj:
```bash
docker-compose down -v
docker-compose up -d --build
Get-Content ./DataBase/01_schema.sql | docker exec -i skysecure_db psql -U skysecure_user -d skysecure_db
Get-Content ./DataBase/02_seed.sql | docker exec -i skysecure_db psql -U skysecure_user -d skysecure_db
```
(Flaga -v jest wymagana do wyczyszczenia starych wolumenow i zaladowania nowych danych testowych z plikow .sql).

### Krok 3: Weryfikacja API
Poczekaj 10-15 sekund na inicjalizacje bazy, a nastepnie otworz:
http://localhost/api/docs

### Krok 4: Uruchomienie aplikacji klienckiej
Otworz menedzer plikow, wejdz do folderu FrontEnd i kliknij dwukrotnie plik main.html (otworzy sie w przegladarce).

### Krok 5: Testowanie logowania
Mozesz zarejestrowac nowego uzytkownika przez interfejs lub uzyc gotowego konta z bazy:
* Email: admin@skysecure.pl lub test@skysecure.pl
* Haslo: SuperSecretPassword123

---

## Struktura Bazy Danych
System operuje obecnie na 3 polaczonych relacyjnie tabelach:
1. **Uzytkownicy**: Dane osobowe, haslo (Argon2), rola.
2. **Lotniska**: kod_iata (np. WAW, LUZ), nazwa, miasto, kraj.
3. **Loty**: numer_lotu, klucze obce do lotnisk (odlot/przylot), czasy, cena, liczba_miejsc.
