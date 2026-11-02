CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Users
CREATE TABLE uzytkownicy (
    id_uzytkownika INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nazwisko VARCHAR(50) NOT NULL,
    imie VARCHAR(30) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    haslo_hash VARCHAR(255) NOT NULL,
    rola VARCHAR(20) NOT NULL DEFAULT 'User',
    data_rejestracji TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Airports
CREATE TABLE lotniska (
    id_lotniska INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kod_iata VARCHAR(3) UNIQUE NOT NULL,
    nazwa VARCHAR(100) NOT NULL,
    miasto VARCHAR(100) NOT NULL,
    kraj VARCHAR(50) NOT NULL
);

-- 3. Flights
CREATE TABLE loty (
    id_lotu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numer_lotu VARCHAR(10) UNIQUE NOT NULL,
    id_lotniska_odlotu INTEGER NOT NULL REFERENCES lotniska(id_lotniska) ON DELETE CASCADE,
    id_lotniska_przylotu INTEGER NOT NULL REFERENCES lotniska(id_lotniska) ON DELETE CASCADE,
    czas_odlotu TIMESTAMP NOT NULL,
    czas_przylotu TIMESTAMP NOT NULL,
    cena DECIMAL(10, 2) NOT NULL,
    liczba_miejsc INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Zaplanowany'
);

-- 4. Seats
CREATE TABLE miejsca (
    id_miejsca INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_lotu INTEGER NOT NULL REFERENCES loty(id_lotu) ON DELETE CASCADE,
    numer_miejsca VARCHAR(5) NOT NULL,
    klasa VARCHAR(20) DEFAULT 'Economy',
    czy_wolne BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_lot_miejsce UNIQUE(id_lotu, numer_miejsca)
);

-- 5. Bookings
CREATE TABLE rezerwacje (
    id_rezerwacji INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_uzytkownika INTEGER NOT NULL REFERENCES uzytkownicy(id_uzytkownika) ON DELETE CASCADE,
    id_lotu INTEGER NOT NULL REFERENCES loty(id_lotu) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'Oczekująca',
    kwota_laczna DECIMAL(10, 2) NOT NULL,
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tickets
CREATE TABLE bilety (
    id_biletu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_rezerwacji INTEGER NOT NULL REFERENCES rezerwacje(id_rezerwacji) ON DELETE CASCADE,
    id_miejsca INTEGER NOT NULL REFERENCES miejsca(id_miejsca) ON DELETE RESTRICT, 
    imie_pasazera VARCHAR(50) NOT NULL,
    nazwisko_pasazera VARCHAR(50) NOT NULL,
    CONSTRAINT uq_miejsce_bilet UNIQUE(id_miejsca)
);

-- 7. Payments
CREATE TABLE platnosci (
    id_platnosci INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_rezerwacji INTEGER NOT NULL REFERENCES rezerwacje(id_rezerwacji) ON DELETE CASCADE,
    kwota DECIMAL(10, 2) NOT NULL,
    status_transakcji VARCHAR(20) DEFAULT 'Pending',
    metoda VARCHAR(50) NOT NULL,
    data_transakcji TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    identyfikator_sesji UUID
);

-- 8. Audit logs
CREATE TABLE logi_audytowe (
    id_logu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_uzytkownika INTEGER REFERENCES uzytkownicy(id_uzytkownika) ON DELETE SET NULL, 
    adres_ip VARCHAR(45),
    akcja VARCHAR(100) NOT NULL, 
    szczegoly TEXT,
    data_zdarzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Automatically generates seats on flight creation
CREATE OR REPLACE FUNCTION generate_seats_for_new_flight()
RETURNS TRIGGER AS $$
DECLARE
    seat_count INT := 0;
    row_num INT := 1;
    col_idx INT := 1;
    cols TEXT[] := ARRAY['A', 'B', 'C', 'D', 'E', 'F'];
BEGIN
    WHILE seat_count < NEW.liczba_miejsc LOOP
        INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
        VALUES (NEW.id_lotu, row_num::TEXT || cols[col_idx], 'Economy', TRUE);
        
        seat_count := seat_count + 1;
        col_idx := col_idx + 1;
        
        IF col_idx > 6 THEN
            col_idx := 1;
            row_num := row_num + 1;
        END IF;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generate_seats_after_insert
AFTER INSERT ON loty
FOR EACH ROW
EXECUTE FUNCTION generate_seats_for_new_flight();
