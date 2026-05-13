-- =============================================================================
-- 02_seed.sql  —  SkySecure Airlines  —  Kompletny seed danych testowych
-- =============================================================================
-- Hasło dla WSZYSTKICH kont testowych: SuperSecretPassword123
-- Hash argon2id wygenerowany przez aplikację (auth_utils.py → hash_password)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. UŻYTKOWNICY
-- ---------------------------------------------------------------------------
INSERT INTO uzytkownicy (imie, nazwisko, email, haslo_hash, rola) VALUES
('Admin',    'Systemu',    'admin@skysecure.pl',    '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'Admin'),
('Testowy',  'Pasażer',   'test@skysecure.pl',     '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User'),
('Anna',     'Kowalska',  'anna.kowalska@mail.pl', '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User'),
('Piotr',   'Wiśniewski','piotr.w@mail.pl',        '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User'),
('Maria',    'Nowak',     'maria.nowak@mail.pl',   '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User');


-- ---------------------------------------------------------------------------
-- 2. LOTNISKA
-- ---------------------------------------------------------------------------
INSERT INTO lotniska (kod_iata, nazwa, miasto, kraj) VALUES
('WAW', 'Lotnisko Chopina',              'Warszawa', 'Polska'),
('LUZ', 'Port Lotniczy Lublin',          'Lublin',   'Polska'),
('LHR', 'Heathrow',                      'Londyn',   'Wielka Brytania'),
('JFK', 'John F. Kennedy International', 'Nowy Jork','USA'),
('CDG', 'Charles de Gaulle',             'Paryż',    'Francja'),
('FRA', 'Frankfurt am Main',             'Frankfurt','Niemcy'),
('AMS', 'Amsterdam Airport Schiphol',    'Amsterdam','Holandia');


-- ---------------------------------------------------------------------------
-- 3. LOTY
--    liczba_miejsc musi zgadzać się z rzeczywistą mapą pokładu (patrz niżej)
--    SK1001: 250 miejsc  (8 First + 42 Business + 200 Economy)
--    SK1002: 180 miejsc  (0 First + 20 Business + 160 Economy)
--    SK1003: 200 miejsc  (0 First + 30 Business + 170 Economy)
--    SK1004: 180 miejsc  (0 First + 20 Business + 160 Economy)
--    SK1005:  90 miejsc  (0 First + 10 Business +  80 Economy)  ← lot dodatkowy
--    SK1006: 120 miejsc  (0 First + 15 Business + 105 Economy)  ← lot dodatkowy
-- ---------------------------------------------------------------------------
INSERT INTO loty (numer_lotu, id_lotniska_odlotu, id_lotniska_przylotu,
                  czas_odlotu, czas_przylotu, cena, liczba_miejsc, status)
VALUES
-- SK1001  WAW → JFK  (Boeing 777, 250 pax)
('SK1001',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'JFK'),
 '2026-06-10 10:00:00', '2026-06-10 19:30:00',
 2500.00, 250, 'Zaplanowany'),

-- SK1002  LUZ → LHR  (Airbus A320, 180 pax)
('SK1002',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LUZ'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'),
 '2026-06-12 18:00:00', '2026-06-12 19:45:00',
 450.00, 180, 'Zaplanowany'),

-- SK1003  WAW → CDG  (Airbus A321, 200 pax)
('SK1003',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'CDG'),
 '2026-06-15 08:00:00', '2026-06-15 10:15:00',
 600.00, 200, 'Zaplanowany'),

-- SK1004  LHR → WAW  (Airbus A320, 180 pax)
('SK1004',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 '2026-06-20 12:00:00', '2026-06-20 15:30:00',
 550.00, 180, 'Zaplanowany'),

-- SK1005  WAW → FRA  (Embraer 195, 90 pax) ← mniejszy samolot dla testów
('SK1005',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'FRA'),
 '2026-06-25 06:30:00', '2026-06-25 08:00:00',
 320.00, 90, 'Zaplanowany'),

-- SK1006  CDG → AMS  (Boeing 737, 120 pax)
('SK1006',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'CDG'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'AMS'),
 '2026-07-01 14:00:00', '2026-07-01 15:10:00',
 280.00, 120, 'Zaplanowany'),

-- SK1007  WAW → LHR  ← lot ZAKOŃCZONY (do testów historii / panelu admina)
('SK1007',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'),
 '2026-05-01 07:00:00', '2026-05-01 08:50:00',
 400.00, 150, 'Zakończony'),

-- SK1008  JFK → WAW  ← lot ODWOŁANY (do testów filtrowania)
('SK1008',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'JFK'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 '2026-06-18 22:00:00', '2026-06-19 12:00:00',
 2800.00, 250, 'Odwołany');


-- =============================================================================
-- 4. MIEJSCA  —  KLUCZOWA CZĘŚĆ
--    Każdy lot musi mieć DOKŁADNIE tyle wierszy w tabeli 'miejsca',
--    ile wynosi pole liczba_miejsc w tabeli 'loty'.
--
--    Konwencja numeracji (standard lotniczy):
--      Rząd 1-2      → First Class    (kolumny A, C, D, F  — szeroki układ 2-2)
--      Rząd 3-9      → Business       (kolumny A, C, D, F  — układ 2-2)
--      Rząd 10-99    → Economy        (kolumny A, B, C, D, E, F — układ 3-3)
--
--    Używamy funkcji generate_series() PostgreSQL — nie piszemy 250 INSERTów ręcznie!
-- =============================================================================

-- ---------------------------------------------------------------------------
-- POMOCNICZA FUNKCJA: generate_seat_number(rzad, kolumna) → VARCHAR
--   Zwraca np. '12A', '1C', '34F'
-- (Tymczasowa funkcja — usuwana na końcu skryptu)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION _seed_seat(r INT, c TEXT) RETURNS VARCHAR AS $$
BEGIN RETURN CAST(r AS TEXT) || c; END;
$$ LANGUAGE plpgsql;


-- ===========================================================================
-- SK1001  —  250 miejsc  (8 First + 42 Business + 200 Economy)
--   First:    rzędy 1-2,   kolumny A C D F  → 2 × 4 = 8
--   Business: rzędy 3-12,  kolumny A C D F  → 10 × 4 = 40  (razem do 48, ale mamy 42 — korekta: rząd 3-11 = 9×4=36 + rząd 12 = 6 kol = nie pasuje)
--   Proste podejście: Business rzędy 3-12, kolumny A B C D E F = 10×6 = 60 — za dużo
--   Używamy realnego podziału: First 1-2 (4 kol), Business 3-9 (6 kol = 42), Economy 10-43 (6 kol = 200)
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
-- First Class: rzędy 1-2, 4 kolumny (A C D F)
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
    _seed_seat(r, c),
    'First',
    TRUE
FROM generate_series(1, 2) AS r,
     unnest(ARRAY['A','C','D','F']) AS c

UNION ALL

-- Business: rzędy 3-9, 6 kolumn (A B C D E F) → 7 × 6 = 42
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
    _seed_seat(r, c),
    'Business',
    TRUE
FROM generate_series(3, 9) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

-- Economy: rzędy 10-43, 6 kolumn → 34 × 6 = 204... korygujemy do rzędów 10-42 → 33×6=198 + rząd 43 kolumny A B → 200
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
    _seed_seat(r, c),
    'Economy',
    TRUE
FROM generate_series(10, 42) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
    _seed_seat(43, c),
    'Economy',
    TRUE
FROM unnest(ARRAY['A','B']) AS c;

-- Weryfikacja: SELECT COUNT(*) FROM miejsca WHERE id_lotu=(SELECT id_lotu FROM loty WHERE numer_lotu='SK1001');
-- Oczekiwany wynik: 8 + 42 + 200 = 250 ✓


-- ===========================================================================
-- SK1002  —  180 miejsc  (20 Business + 160 Economy)
--   Business: rzędy 1-4,  6 kolumn → 4 × 5 = 20 (4×5 bo kolumny A B C D E)
--   Proste: Business rzędy 1-4, 5 kol (A B C D E) = 20. Economy rzędy 5-31, 6 kol = 27×6=162... → rzędy 5-30 = 26×6=156 + rząd 31 A B C D = 160. Razem 20+160=180 ✓
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
-- Business: rzędy 1-4, 5 kolumn
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002'),
    _seed_seat(r, c),
    'Business',
    TRUE
FROM generate_series(1, 4) AS r,
     unnest(ARRAY['A','B','C','D','E']) AS c

UNION ALL

-- Economy: rzędy 5-30, 6 kolumn = 156
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002'),
    _seed_seat(r, c),
    'Economy',
    TRUE
FROM generate_series(5, 30) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

-- Economy: rząd 31, 4 kolumny = 4 → łącznie 156+4=160 Economy
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002'),
    _seed_seat(31, c),
    'Economy',
    TRUE
FROM unnest(ARRAY['A','B','C','D']) AS c;

-- Weryfikacja: 20 + 156 + 4 = 180 ✓


-- ===========================================================================
-- SK1003  —  200 miejsc  (30 Business + 170 Economy)
--   Business: rzędy 1-5, 6 kolumn = 30
--   Economy: rzędy 6-33, 6 kolumn = 28×6=168 + rząd 34 A B = 2 → 170. Razem 200 ✓
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1003'),
    _seed_seat(r, c),
    'Business',
    TRUE
FROM generate_series(1, 5) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1003'),
    _seed_seat(r, c),
    'Economy',
    TRUE
FROM generate_series(6, 33) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1003'),
    _seed_seat(34, c),
    'Economy',
    TRUE
FROM unnest(ARRAY['A','B']) AS c;

-- Weryfikacja: 30 + 168 + 2 = 200 ✓


-- ===========================================================================
-- SK1004  —  180 miejsc  (identyczny układ jak SK1002)
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1004'),
    _seed_seat(r, c),
    'Business',
    TRUE
FROM generate_series(1, 4) AS r,
     unnest(ARRAY['A','B','C','D','E']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1004'),
    _seed_seat(r, c),
    'Economy',
    TRUE
FROM generate_series(5, 30) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1004'),
    _seed_seat(31, c),
    'Economy',
    TRUE
FROM unnest(ARRAY['A','B','C','D']) AS c;

-- Weryfikacja: 180 ✓


-- ===========================================================================
-- SK1005  —  90 miejsc  (10 Business + 80 Economy)
--   Business: rzędy 1-2, 5 kolumn = 10
--   Economy: rzędy 3-15, 6 kolumn = 13×6=78 + rząd 16 A B = 2 → 80. Razem 90 ✓
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1005'),
    _seed_seat(r, c),
    'Business',
    TRUE
FROM generate_series(1, 2) AS r,
     unnest(ARRAY['A','B','C','D','E']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1005'),
    _seed_seat(r, c),
    'Economy',
    TRUE
FROM generate_series(3, 15) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1005'),
    _seed_seat(16, c),
    'Economy',
    TRUE
FROM unnest(ARRAY['A','B']) AS c;

-- Weryfikacja: 10 + 78 + 2 = 90 ✓


-- ===========================================================================
-- SK1006  —  120 miejsc  (15 Business + 105 Economy)
--   Business: rzędy 1-3, 5 kolumn = 15
--   Economy: rzędy 4-21, 6 kolumn = 18×6=108... → rzędy 4-20 = 17×6=102 + rząd 21 A B C = 3 → 105. Razem 120 ✓
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1006'),
    _seed_seat(r, c),
    'Business',
    TRUE
FROM generate_series(1, 3) AS r,
     unnest(ARRAY['A','B','C','D','E']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1006'),
    _seed_seat(r, c),
    'Economy',
    TRUE
FROM generate_series(4, 20) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1006'),
    _seed_seat(21, c),
    'Economy',
    TRUE
FROM unnest(ARRAY['A','B','C']) AS c;

-- Weryfikacja: 15 + 102 + 3 = 120 ✓


-- ===========================================================================
-- SK1007  —  150 miejsc ZAKOŃCZONY  (15 Business + 135 Economy)
--   Business: rzędy 1-3, 5 kolumn = 15
--   Economy: rzędy 4-25, 6 kolumn = 22×6=132 + rząd 26 A B C = 3 → 135. Razem 150 ✓
--   UWAGA: wszystkie miejsca są ZAJĘTE (lot zakończony — potrzebne do testów historii)
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1007'),
    _seed_seat(r, c),
    'Business',
    FALSE   -- lot zakończony, wszystkie miejsca zajęte
FROM generate_series(1, 3) AS r,
     unnest(ARRAY['A','B','C','D','E']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1007'),
    _seed_seat(r, c),
    'Economy',
    FALSE
FROM generate_series(4, 25) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1007'),
    _seed_seat(26, c),
    'Economy',
    FALSE
FROM unnest(ARRAY['A','B','C']) AS c;

-- Weryfikacja: 15 + 132 + 3 = 150 ✓


-- ===========================================================================
-- SK1008  —  250 miejsc ODWOŁANY  (identyczny układ jak SK1001)
--            Wszystkie miejsca wolne (lot odwołany przed odprawą)
-- ===========================================================================
INSERT INTO miejsca (id_lotu, numer_miejsca, klasa, czy_wolne)
SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1008'),
    _seed_seat(r, c),
    'First',
    TRUE
FROM generate_series(1, 2) AS r,
     unnest(ARRAY['A','C','D','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1008'),
    _seed_seat(r, c),
    'Business',
    TRUE
FROM generate_series(3, 9) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1008'),
    _seed_seat(r, c),
    'Economy',
    TRUE
FROM generate_series(10, 42) AS r,
     unnest(ARRAY['A','B','C','D','E','F']) AS c

UNION ALL

SELECT
    (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1008'),
    _seed_seat(43, c),
    'Economy',
    TRUE
FROM unnest(ARRAY['A','B']) AS c;

-- Weryfikacja: 250 ✓


-- ===========================================================================
-- Usuwamy pomocniczą funkcję
-- ===========================================================================
DROP FUNCTION IF EXISTS _seed_seat(INT, TEXT);


-- ---------------------------------------------------------------------------
-- 5. REZERWACJE — różne statusy dla pełnych testów
-- ---------------------------------------------------------------------------
INSERT INTO rezerwacje (id_uzytkownika, id_lotu, status, kwota_laczna) VALUES

-- [1] Testowy Pasażer — SK1001 — Opłacona (główny scenariusz happy path)
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
 'Opłacona', 2500.00),

-- [2] Testowy Pasażer — SK1003 — Oczekująca (niepłacona, dla testu flow płatności)
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1003'),
 'Oczekująca', 600.00),

-- [3] Anna Kowalska — SK1002 — Opłacona
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002'),
 'Opłacona', 450.00),

-- [4] Piotr Wiśniewski — SK1001 — Opłacona (kilka rezerwacji na ten sam lot)
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
 'Opłacona', 2500.00),

-- [5] Piotr Wiśniewski — SK1005 — Anulowana (test statusu Anulowana)
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1005'),
 'Anulowana', 320.00),

-- [6] Maria Nowak — SK1004 — Oczekująca
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'maria.nowak@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1004'),
 'Oczekująca', 550.00);


-- ---------------------------------------------------------------------------
-- 6. BILETY — przypisujemy pasażerów do konkretnych miejsc
--    Zajmujemy konkretne miejsca i aktualizujemy czy_wolne = FALSE
-- ---------------------------------------------------------------------------

-- Rezerwacja [1]: Testowy Pasażer — SK1001 — miejsce 1A (First)
INSERT INTO bilety (id_rezerwacji, id_miejsca, imie_pasazera, nazwisko_pasazera)
VALUES (
    1,
    (SELECT id_miejsca FROM miejsca
     WHERE id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001')
       AND numer_miejsca = '1A'),
    'Testowy', 'Pasażer'
);
UPDATE miejsca SET czy_wolne = FALSE
WHERE id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001')
  AND numer_miejsca = '1A';

-- Rezerwacja [3]: Anna Kowalska — SK1002 — miejsce 1A (Business)
INSERT INTO bilety (id_rezerwacji, id_miejsca, imie_pasazera, nazwisko_pasazera)
VALUES (
    3,
    (SELECT id_miejsca FROM miejsca
     WHERE id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002')
       AND numer_miejsca = '1A'),
    'Anna', 'Kowalska'
);
UPDATE miejsca SET czy_wolne = FALSE
WHERE id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002')
  AND numer_miejsca = '1A';

-- Rezerwacja [4]: Piotr Wiśniewski — SK1001 — miejsce 10A (Economy)
INSERT INTO bilety (id_rezerwacji, id_miejsca, imie_pasazera, nazwisko_pasazera)
VALUES (
    4,
    (SELECT id_miejsca FROM miejsca
     WHERE id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001')
       AND numer_miejsca = '10A'),
    'Piotr', 'Wiśniewski'
);
UPDATE miejsca SET czy_wolne = FALSE
WHERE id_lotu = (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001')
  AND numer_miejsca = '10A';

-- Uwaga: rezerwacja [2] i [6] są Oczekujące — bilety jeszcze nie wystawione
-- Rezerwacja [5] jest Anulowana — bilet nie wystawiony


-- ---------------------------------------------------------------------------
-- 7. PŁATNOŚCI
-- ---------------------------------------------------------------------------
INSERT INTO platnosci (id_rezerwacji, kwota, status_transakcji, metoda, identyfikator_sesji) VALUES
-- Rezerwacja [1] — BLIK — sukces
(1, 2500.00, 'Success', 'BLIK',   gen_random_uuid()),
-- Rezerwacja [3] — Karta — sukces
(3,  450.00, 'Success', 'Karta',  gen_random_uuid()),
-- Rezerwacja [4] — ApplePay — sukces
(4, 2500.00, 'Success', 'ApplePay', gen_random_uuid()),
-- Rezerwacja [5] (anulowana) — Karta — pierwotna próba się nie powiodła
(5,  320.00, 'Failed',  'Karta',  gen_random_uuid());


-- ---------------------------------------------------------------------------
-- 8. LOGI AUDYTOWE — bogata historia dla testów panelu admina
-- ---------------------------------------------------------------------------
INSERT INTO logi_audytowe (id_uzytkownika, adres_ip, akcja, szczegoly) VALUES

-- Logi logowania
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'admin@skysecure.pl'),
 '10.0.0.1', 'LOGIN_SUCCESS', 'Admin zalogował się do systemu'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'LOGIN_SUCCESS', 'Pomyślne logowanie'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'LOGIN_SUCCESS', 'Pomyślne logowanie'),

-- Nieudane próby (brute-force symulacja)
(NULL, '103.45.67.89', 'LOGIN_FAILED', 'Próba ataku brute-force na konto admin@skysecure.pl'),
(NULL, '103.45.67.89', 'LOGIN_FAILED', 'Kolejna nieudana próba logowania z tego samego IP'),
(NULL, '103.45.67.90', 'LOGIN_FAILED', 'Próba SQL injection w polu email'),

-- Logi rezerwacji
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'RESERVATION_CREATED', 'Utworzono rezerwację na lot SK1001'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'RESERVATION_CREATED', 'Utworzono rezerwację na lot SK1002'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 '91.200.44.22', 'RESERVATION_CREATED', 'Utworzono rezerwację na lot SK1001'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 '91.200.44.22', 'RESERVATION_CANCELLED', 'Anulowano rezerwację na lot SK1005'),

-- Logi płatności
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'PAYMENT_SUCCESS', 'Zaksięgowano płatność 2500.00 PLN metodą BLIK dla rezerwacji 1'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'PAYMENT_SUCCESS', 'Zaksięgowano płatność 450.00 PLN metodą Karta dla rezerwacji 3'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 '91.200.44.22', 'PAYMENT_FAILED', 'Nieudana płatność 320.00 PLN metodą Karta dla rezerwacji 5'),

-- Logi biletów
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'TICKET_ISSUED', 'Wystawiono bilet dla rezerwacji 1, miejsce 1A (First)'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'TICKET_ISSUED', 'Wystawiono bilet dla rezerwacji 3, miejsce 1A (Business)'),

-- Log admina — zarządzanie lotem
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'admin@skysecure.pl'),
 '10.0.0.1', 'FLIGHT_STATUS_CHANGED', 'Lot SK1007 zmienił status na Zakończony'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'admin@skysecure.pl'),
 '10.0.0.1', 'FLIGHT_STATUS_CHANGED', 'Lot SK1008 zmienił status na Odwołany');


-- =============================================================================
-- WERYFIKACJA KOŃCOWA (możesz uruchomić ręcznie po seedowaniu)
-- =============================================================================
-- SELECT
--     l.numer_lotu,
--     l.liczba_miejsc AS zadeklarowane,
--     COUNT(m.id_miejsca) AS w_bazie,
--     l.liczba_miejsc - COUNT(m.id_miejsca) AS roznica
-- FROM loty l
-- LEFT JOIN miejsca m ON m.id_lotu = l.id_lotu
-- GROUP BY l.numer_lotu, l.liczba_miejsc
-- ORDER BY l.numer_lotu;
-- Oczekiwany wynik: kolumna "roznica" = 0 dla WSZYSTKICH lotów.
-- =============================================================================