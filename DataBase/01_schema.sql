CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1.  Użytkownicy 
CREATE TABLE Uzytkownicy (
    id_uzytkownika INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nazwisko VARCHAR(50) NOT NULL,
    imie VARCHAR(30) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    haslo_hash VARCHAR(255) NOT NULL,
    rola VARCHAR(20) NOT NULL DEFAULT 'User',
    data_rejestracji TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Lotniska 
CREATE TABLE Lotniska (
    id_lotniska INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kod_iata VARCHAR(3) UNIQUE NOT NULL, -- np. WAW, LUZ, JFK
    nazwa VARCHAR(100) NOT NULL,
    miasto VARCHAR(100) NOT NULL,
    kraj VARCHAR(50) NOT NULL
);

-- 3. Loty 
CREATE TABLE Loty (
    id_lotu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numer_lotu VARCHAR(10) UNIQUE NOT NULL, -- np. SK101
    id_lotniska_odlotu INTEGER NOT NULL REFERENCES Lotniska(id_lotniska) ON DELETE CASCADE,
    id_lotniska_przylotu INTEGER NOT NULL REFERENCES Lotniska(id_lotniska) ON DELETE CASCADE,
    czas_odlotu TIMESTAMP NOT NULL,
    czas_przylotu TIMESTAMP NOT NULL,
    cena DECIMAL(10, 2) NOT NULL,
    liczba_miejsc INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Zaplanowany' -- Zaplanowany, W trakcie, Zakończony, Odwołany
);