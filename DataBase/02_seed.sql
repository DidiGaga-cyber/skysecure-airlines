-- 1. Seeding danych (Wypełnianie bazy testowymi użytkownikami)
-- Uwaga: Hasło dla wszystkich testowych kont to: SuperSecretPassword123
INSERT INTO uzytkownicy (imie, nazwisko, email, haslo_hash, rola) VALUES
('Admin', 'Systemu', 'admin@skysecure.pl', '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'Admin'),
('Testowy', 'Pasażer', 'test@skysecure.pl', '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User');


-- Wypełnianie bazy testowymi lotniskami
INSERT INTO lotniska (kod_iata, nazwa, miasto, kraj) VALUES
('WAW', 'Lotnisko Chopina', 'Warszawa', 'Polska'),
('LUZ', 'Port Lotniczy Lublin', 'Lublin', 'Polska'),
('LHR', 'Heathrow', 'Londyn', 'Wielka Brytania'),
('JFK', 'John F. Kennedy International', 'Nowy Jork', 'USA'),
('CDG', 'Charles de Gaulle', 'Paryż', 'Francja');

-- Wypełnianie bazy testowymi lotami
INSERT INTO loty (numer_lotu, id_lotniska_odlotu, id_lotniska_przylotu, czas_odlotu, czas_przylotu, cena, liczba_miejsc, status) VALUES
('SK1001', (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'), (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'JFK'), '2026-05-10 10:00:00', '2026-05-10 14:30:00', 2500.00, 250, 'Zaplanowany'),
('SK1002', (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LUZ'), (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'), '2026-05-12 18:00:00', '2026-05-12 19:45:00', 450.00, 180, 'Zaplanowany'),
('SK1003', (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'), (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'CDG'), '2026-05-15 08:00:00', '2026-05-15 10:15:00', 600.00, 200, 'Zaplanowany'),
('SK1004', (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'), (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'), '2026-05-20 12:00:00', '2026-05-20 15:30:00', 550.00, 180, 'Zaplanowany');


-- 1. Dodajemy testowe miejsca do lotu z Warszawy do Nowego Jorku (SK1001) i z Lublina (SK1002)
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne) VALUES
((SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'), '1A', 'Business', FALSE),
((SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'), '1B', 'Business', TRUE),
((SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'), '12A', 'Economy', FALSE),
((SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'), '12B', 'Economy', TRUE),
((SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002'), '1A', 'Business', TRUE);

-- 2. Tworzymy testową rezerwację dla naszego Testowego Pasażera
INSERT INTO rezerwacje (id_uzytkownika, id_lotu, status, kwota_laczna) VALUES
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'), 
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'), 
 'Opłacona', 2500.00);

-- 3. Generujemy bilety dla tej rezerwacji (Używamy Posiomu Szyfrowania AES-256 dla paszportu!)
-- Używamy klucza 'SkySecureKey2026' do zaszyfrowania danych w locie
INSERT INTO bilety (id_rezerwacji, id_miejsca, imie_pasazera, nazwisko_pasazera, dane_paszportowe) VALUES
(
    (SELECT id_rezerwacji FROM rezerwacje LIMIT 1),
    (SELECT id_miejsca FROM miejsca WHERE numer_miejsca = '12A' AND id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001')),
    'Testowy', 'Pasażer',
    pgp_sym_encrypt('AA1234567', 'SkySecureKey2026')
),
(
    (SELECT id_rezerwacji FROM rezerwacje LIMIT 1),
    (SELECT id_miejsca FROM miejsca WHERE numer_miejsca = '1A' AND id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001')),
    'Jan', 'Kowalski',
    pgp_sym_encrypt('BB9876543', 'SkySecureKey2026')
);

-- 4. Symulacja udanej płatności (Generujemy losowy identyfikator sesji UUID!)
INSERT INTO platnosci (id_rezerwacji, kwota, status_transakcji, metoda, identyfikator_sesji) VALUES
((SELECT id_rezerwacji FROM rezerwacje LIMIT 1), 2500.00, 'Success', 'BLIK', gen_random_uuid());

-- 5. Wypełniamy logi audytowe (Pokazujemy, że system czuwa)
INSERT INTO logi_audytowe (id_uzytkownika, adres_ip, akcja, szczegoly) VALUES
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'), '192.168.1.15', 'LOGIN_SUCCESS', 'Pomyślne logowanie do systemu'),
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'), '192.168.1.15', 'RESERVATION_CREATED', 'Utworzono rezerwację na lot SK1001 z płatnością BLIK'),
(NULL, '103.45.67.89', 'LOGIN_FAILED', 'Próba ataku brute-force na konto admin@skysecure.pl');

