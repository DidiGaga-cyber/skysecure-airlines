CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1.  Użytkownicy 
CREATE TABLE uzytkownicy (
    id_uzytkownika INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nazwisko VARCHAR(50) NOT NULL,
    imie VARCHAR(30) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    haslo_hash VARCHAR(255) NOT NULL,
    rola VARCHAR(20) NOT NULL DEFAULT 'User',
    data_rejestracji TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Lotniska 
CREATE TABLE lotniska (
    id_lotniska INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kod_iata VARCHAR(3) UNIQUE NOT NULL, -- np. WAW, LUZ, JFK
    nazwa VARCHAR(100) NOT NULL,
    miasto VARCHAR(100) NOT NULL,
    kraj VARCHAR(50) NOT NULL
);

-- 3. Loty 
CREATE TABLE loty (
    id_lotu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numer_lotu VARCHAR(10) UNIQUE NOT NULL, -- np. SK101
    id_lotniska_odlotu INTEGER NOT NULL REFERENCES lotniska(id_lotniska) ON DELETE CASCADE,
    id_lotniska_przylotu INTEGER NOT NULL REFERENCES lotniska(id_lotniska) ON DELETE CASCADE,
    czas_odlotu TIMESTAMP NOT NULL,
    czas_przylotu TIMESTAMP NOT NULL,
    cena DECIMAL(10, 2) NOT NULL,
    liczba_miejsc INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Zaplanowany' -- Zaplanowany, W trakcie, Zakończony, Odwołany
);


-- SPRINT 4: Rezerwacje, Bilety i Miejsca 

-- 1. Tabela Miejsc (Fizyczna mapa pokładu dla każdego lotu)
-- Zamiast trzymać miejsca w JSON, relacyjna tabela pozwala łatwo filtrować wolne fotele.
CREATE TABLE miejsca (
    id_miejsca INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_lotu INTEGER NOT NULL REFERENCES loty(id_lotu) ON DELETE CASCADE,
    numer_miejsca VARCHAR(5) NOT NULL, -- np. "12A", "1A"
    klasa VARCHAR(20) DEFAULT 'Economy', -- Economy, Business, First
    czy_wolne BOOLEAN DEFAULT TRUE,
    -- GWARANCJA BAZY: Na jednym locie nie może być dwóch takich samych miejsc!
    CONSTRAINT uq_lot_miejsce UNIQUE(id_lotu, numer_miejsca)
);

-- 2. Tabela Rezerwacji (Zamówienie - może zawierać kilka biletów)
-- Rozdzielam "Koszyk/Zamówienie" od samego "Biletu", bo ktoś może kupić bilety dla całej rodziny.
CREATE TABLE rezerwacje (
    id_rezerwacji INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_uzytkownika INTEGER NOT NULL REFERENCES uzytkownicy(id_uzytkownika) ON DELETE CASCADE,
    id_lotu INTEGER NOT NULL REFERENCES loty(id_lotu) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'Oczekująca', -- Oczekująca, Opłacona, Anulowana
    kwota_laczna DECIMAL(10, 2) NOT NULL,
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela Biletów (Pasażerowie przypisani do konkretnego miejsca)
CREATE TABLE bilety (
    id_biletu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_rezerwacji INTEGER NOT NULL REFERENCES rezerwacje(id_rezerwacji) ON DELETE CASCADE,
    -- ON DELETE RESTRICT: Nie pozwolimy usunąć miejsca, jeśli jest na nie wystawiony bilet.
    id_miejsca INTEGER NOT NULL REFERENCES miejsca(id_miejsca) ON DELETE RESTRICT, 
    imie_pasazera VARCHAR(50) NOT NULL,
    nazwisko_pasazera VARCHAR(50) NOT NULL,
    -- ZASZYFROWANE DANE: Tutaj wpadnie AES-256 z pgcrypto w Sprincie 5 (dlatego typ BYTEA - binarne).
    
    --dane_paszportowe BYTEA, -- Not needed. Reservation doesn't requeire passport data anymore.

    -- GWARANCJA BAZY: Jedno fizyczne miejsce w samolocie = maksymalnie jeden bilet.
    CONSTRAINT uq_miejsce_bilet UNIQUE(id_miejsca)
);

-- SPRINT 5: Płatności

-- 4. Tabela Płatności (Śledzenie transakcji finansowych)
-- tip: Trzymamy historię płatności z unikalnym UUID sesji dla symulacji bramek (PayU/Stripe).
CREATE TABLE platnosci (
    id_platnosci INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_rezerwacji INTEGER NOT NULL REFERENCES rezerwacje(id_rezerwacji) ON DELETE CASCADE,
    kwota DECIMAL(10, 2) NOT NULL,
    status_transakcji VARCHAR(20) DEFAULT 'Pending', -- Pending, Success, Failed
    metoda VARCHAR(50) NOT NULL, -- np. Karta, BLIK
    data_transakcji TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    identyfikator_sesji UUID -- Idealne do mockowania UC-5
);

-- SPRINT 7: Bezpieczeństwo i Audyt (OWASP)

-- 5. Logi Audytowe (Śledzenie aktywności w systemie)
-- tip: "ON DELETE SET NULL". Jeśli usuniemy hakera z bazy, jego logi MUSZĄ zostać dla prokuratury!
CREATE TABLE logi_audytowe (
    id_logu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_uzytkownika INTEGER REFERENCES uzytkownicy(id_uzytkownika) ON DELETE SET NULL, 
    adres_ip VARCHAR(45), -- 45 znaków pokrywa standard IPv6
    akcja VARCHAR(100) NOT NULL, -- np. 'LOGIN_FAILED', 'RESERVATION_CREATED'
    szczegoly TEXT,
    data_zdarzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);