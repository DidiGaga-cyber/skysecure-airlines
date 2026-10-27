CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Użytkownicy 
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
CREATE TABLE miejsca (
    id_miejsca INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_lotu INTEGER NOT NULL REFERENCES loty(id_lotu) ON DELETE CASCADE,
    numer_miejsca VARCHAR(5) NOT NULL, -- np. "12A", "1A"
    klasa VARCHAR(20) DEFAULT 'Economy', -- Economy, Business, First
    czy_wolne BOOLEAN DEFAULT TRUE,
    CONSTRAINT uq_lot_miejsce UNIQUE(id_lotu, numer_miejsca)
);

-- 2. Tabela Rezerwacji (Zamówienie - może zawierać kilka biletów)
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
    id_miejsca INTEGER NOT NULL REFERENCES miejsca(id_miejsca) ON DELETE RESTRICT, 
    imie_pasazera VARCHAR(50) NOT NULL,
    nazwisko_pasazera VARCHAR(50) NOT NULL,
    CONSTRAINT uq_miejsce_bilet UNIQUE(id_miejsca)
);

-- SPRINT 5: Płatności

-- 4. Tabela Płatności (Śledzenie transakcji finansowych)
CREATE TABLE platnosci (
    id_platnosci INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_rezerwacji INTEGER NOT NULL REFERENCES rezerwacje(id_rezerwacji) ON DELETE CASCADE,
    kwota DECIMAL(10, 2) NOT NULL,
    status_transakcji VARCHAR(20) DEFAULT 'Pending', -- Pending, Success, Failed
    metoda VARCHAR(50) NOT NULL, -- np. Karta, BLIK
    data_transakcji TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    identyfikator_sesji UUID
);

-- SPRINT 7: Bezpieczeństwo i Audyt (OWASP)

-- 5. Logi Audytowe (Śledzenie aktywności w systemie)
CREATE TABLE logi_audytowe (
    id_logu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_uzytkownika INTEGER REFERENCES uzytkownicy(id_uzytkownika) ON DELETE SET NULL, 
    adres_ip VARCHAR(45),
    akcja VARCHAR(100) NOT NULL, 
    szczegoly TEXT,
    data_zdarzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- АВТОМАТИЧЕСКАЯ ГЕНЕРАЦИЯ МЕСТ ДЛЯ НОВЫХ РЕЙСОВ
-- =============================================================================

-- Функция, которая создает места на основе колонки liczba_miejsc
CREATE OR REPLACE FUNCTION generate_seats_for_new_flight()
RETURNS TRIGGER AS $$
DECLARE
    seat_count INT := 0;
    row_num INT := 1;
    col_idx INT := 1;
    cols TEXT[] := ARRAY['A', 'B', 'C', 'D', 'E', 'F']; -- Рассадка 3-3 (Economy)
BEGIN
    WHILE seat_count < NEW.liczba_miejsc LOOP
        INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
        VALUES (NEW.id_lotu, row_num::TEXT || cols[col_idx], 'Economy', TRUE);
        
        seat_count := seat_count + 1;
        col_idx := col_idx + 1;
        
        -- Переход на следующий ряд после создания 6 мест в текущем ряду
        IF col_idx > 6 THEN
            col_idx := 1;
            row_num := row_num + 1;
        END IF;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер, срабатывающий после каждого INSERT в таблицу loty
CREATE TRIGGER trg_generate_seats_after_insert
AFTER INSERT ON loty
FOR EACH ROW
EXECUTE FUNCTION generate_seats_for_new_flight();