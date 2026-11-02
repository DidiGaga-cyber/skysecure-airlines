-- Test user password: SuperSecretPassword123 (argon2id)

-- 1. Users
INSERT INTO uzytkownicy (imie, nazwisko, email, haslo_hash, rola) VALUES
('Admin',    'Systemu',    'admin@skysecure.pl',    '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'Admin'),
('Testowy',  'Pasażer',   'test@skysecure.pl',     '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User'),
('Anna',     'Kowalska',  'anna.kowalska@mail.pl', '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User'),
('Piotr',   'Wiśniewski','piotr.w@mail.pl',        '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User'),
('Maria',    'Nowak',     'maria.nowak@mail.pl',   '$argon2id$v=19$m=65536,t=3,p=4$jPEeA6AUQogRovQ+ZwzhfA$eZc2W43e87+/NnzlQ6AlxMZsU0eb7IvCVLCZPTqYmx8', 'User');

-- 2. Airports
INSERT INTO lotniska (kod_iata, nazwa, miasto, kraj) VALUES
('ADD', 'Bole International Airport', 'Addis Ababa', 'Ethiopia'),
('AKL', 'Auckland Airport', 'Auckland', 'New Zealand'),
('AMS', 'Amsterdam Airport Schiphol', 'Amsterdam', 'Holandia'),
('ATL', 'Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'USA'),
('BKK', 'Suvarnabhumi Airport', 'Bangkok', 'Tajlandia'),
('BOG', 'El Dorado International Airport', 'Bogota', 'Kolumbia'),
('BOM', 'Chhatrapati Shivaji Maharaj International Airport', 'Mumbaj', 'Indie'),
('CAI', 'Cairo International Airport', 'Kair', 'Egipt'),
('CDG', 'Charles de Gaulle', 'Paryz', 'Francja'),
('CPH', 'Copenhagen Airport', 'Kopenhaga', 'Dania'),
('CPT', 'Cape Town International Airport', 'Kapsztad', 'RPA'),
('DEL', 'Indira Gandhi International Airport', 'Delhi', 'Indie'),
('DEN', 'Denver International Airport', 'Denver', 'USA'),
('DFW', 'Dallas/Fort Worth International Airport', 'Dallas', 'USA'),
('DOH', 'Hamad International Airport', 'Doha', 'Katar'),
('DXB', 'Dubai International Airport', 'Dubaj', 'ZEA'),
('EZE', 'Ministro Pistarini International Airport', 'Buenos Aires', 'Argentyna'),
('FCO', 'Leonardo da Vinci-Fiumicino Airport', 'Rzym', 'Wlochy'),
('FRA', 'Frankfurt am Main', 'Frankfurt', 'Niemcy'),
('GRU', 'Sao Paulo/Guarulhos International Airport', 'Sao Paulo', 'Brazylia'),
('HKG', 'Hong Kong International Airport', 'Hongkong', 'Chiny'),
('HND', 'Tokyo Haneda Airport', 'Tokio', 'Japonia'),
('ICN', 'Incheon International Airport', 'Seul', 'Korea Poludniowa'),
('JFK', 'John F. Kennedy International', 'Nowy Jork', 'USA'),
('JNB', 'O.R. Tambo International Airport', 'Johannesburg', 'RPA'),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA'),
('LHR', 'Heathrow', 'Londyn', 'Wielka Brytania'),
('LUZ', 'Port Lotniczy Lublin', 'Lublin', 'Polska'),
('MAD', 'Adolfo Suarez Madrid-Barajas Airport', 'Madryt', 'Hiszpania'),
('MEL', 'Melbourne Airport', 'Melbourne', 'Australia'),
('MEX', 'Mexico City International Airport', 'Meksyk', 'Meksyk'),
('MIA', 'Miami International Airport', 'Miami', 'USA'),
('MUC', 'Munich Airport', 'Monachium', 'Niemcy'),
('ORD', 'O''Hare International Airport', 'Chicago', 'USA'),
('SCL', 'Arturo Merino Benitez International Airport', 'Santiago', 'Chile'),
('SFO', 'San Francisco International Airport', 'San Francisco', 'USA'),
('SIN', 'Singapore Changi Airport', 'Singapur', 'Singapur'),
('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia'),
('VIE', 'Vienna International Airport', 'Wieden', 'Austria'),
('WAW', 'Lotnisko Chopina', 'Warszawa', 'Polska'),
('YVR', 'Vancouver International Airport', 'Vancouver', 'Kanada'),
('YYZ', 'Toronto Pearson International Airport', 'Toronto', 'Kanada'),
('ZRH', 'Zurich Airport', 'Zurych', 'Szwajcaria')
ON CONFLICT (kod_iata) DO UPDATE SET nazwa = EXCLUDED.nazwa, miasto = EXCLUDED.miasto, kraj = EXCLUDED.kraj;

-- 3. Flights
INSERT INTO loty (numer_lotu, id_lotniska_odlotu, id_lotniska_przylotu,
                  czas_odlotu, czas_przylotu, cena, liczba_miejsc, status)
VALUES
('SK1001',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'JFK'),
 '2026-06-10 10:00:00', '2026-06-10 19:30:00',
 2500.00, 250, 'Zaplanowany'),

('SK1002',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LUZ'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'),
 '2026-06-12 18:00:00', '2026-06-12 19:45:00',
 450.00, 180, 'Zaplanowany'),

('SK1003',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'CDG'),
 '2026-06-15 08:00:00', '2026-06-15 10:15:00',
 600.00, 200, 'Zaplanowany'),

('SK1004',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 '2026-06-20 12:00:00', '2026-06-20 15:30:00',
 550.00, 180, 'Zaplanowany'),

('SK1005',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'FRA'),
 '2026-06-25 06:30:00', '2026-06-25 08:00:00',
 320.00, 90, 'Zaplanowany'),

('SK1006',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'CDG'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'AMS'),
 '2026-07-01 14:00:00', '2026-07-01 15:10:00',
 280.00, 120, 'Zaplanowany'),

('SK1007',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'LHR'),
 '2026-05-01 07:00:00', '2026-05-01 08:50:00',
 400.00, 150, 'Zakończony'),

('SK1008',
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'JFK'),
 (SELECT id_lotniska FROM lotniska WHERE kod_iata = 'WAW'),
 '2026-06-18 22:00:00', '2026-06-19 12:00:00',
 2800.00, 250, 'Odwołany');

DROP FUNCTION IF EXISTS _seed_seat(INT, TEXT);

-- 4. Bookings
INSERT INTO rezerwacje (id_uzytkownika, id_lotu, status, kwota_laczna) VALUES
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
 'Opłacona', 2500.00),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1003'),
 'Oczekująca', 600.00),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1002'),
 'Opłacona', 450.00),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1001'),
 'Opłacona', 2500.00),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1005'),
 'Anulowana', 320.00),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'maria.nowak@mail.pl'),
 (SELECT id_lotu FROM loty WHERE numer_lotu = 'SK1004'),
 'Oczekująca', 550.00);

-- 5. Tickets
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

-- 6. Payments
INSERT INTO platnosci (id_rezerwacji, kwota, status_transakcji, metoda, identyfikator_sesji) VALUES
(1, 2500.00, 'Success', 'BLIK',   gen_random_uuid()),
(3,  450.00, 'Success', 'Karta',  gen_random_uuid()),
(4, 2500.00, 'Success', 'ApplePay', gen_random_uuid()),
(5,  320.00, 'Failed',  'Karta',  gen_random_uuid());

-- 7. Audit logs
INSERT INTO logi_audytowe (id_uzytkownika, adres_ip, akcja, szczegoly) VALUES
((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'admin@skysecure.pl'),
 '10.0.0.1', 'LOGIN_SUCCESS', 'Admin zalogował się do systemu'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'LOGIN_SUCCESS', 'Pomyślne logowanie'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'LOGIN_SUCCESS', 'Pomyślne logowanie'),

(NULL, '103.45.67.89', 'LOGIN_FAILED', 'Próba ataku brute-force na konto admin@skysecure.pl'),
(NULL, '103.45.67.89', 'LOGIN_FAILED', 'Kolejna nieudana próba logowania z tego samego IP'),
(NULL, '103.45.67.90', 'LOGIN_FAILED', 'Próba SQL injection w polu email'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'RESERVATION_CREATED', 'Utworzono rezerwację na lot SK1001'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'RESERVATION_CREATED', 'Utworzono rezerwację na lot SK1002'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 '91.200.44.22', 'RESERVATION_CREATED', 'Utworzono rezerwację na lot SK1001'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 '91.200.44.22', 'RESERVATION_CANCELLED', 'Anulowano rezerwację na lot SK1005'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'PAYMENT_SUCCESS', 'Zaksięgowano płatność 2500.00 PLN metodą BLIK dla rezerwacji 1'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'PAYMENT_SUCCESS', 'Zaksięgowano płatność 450.00 PLN metodą Karta dla rezerwacji 3'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'piotr.w@mail.pl'),
 '91.200.44.22', 'PAYMENT_FAILED', 'Nieudana płatność 320.00 PLN metodą Karta dla rezerwacji 5'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'test@skysecure.pl'),
 '192.168.1.15', 'TICKET_ISSUED', 'Wystawiono bilet dla rezerwacji 1, miejsce 1A (First)'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'anna.kowalska@mail.pl'),
 '78.32.10.5', 'TICKET_ISSUED', 'Wystawiono bilet dla rezerwacji 3, miejsce 1A (Business)'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'admin@skysecure.pl'),
 '10.0.0.1', 'FLIGHT_STATUS_CHANGED', 'Lot SK1007 zmienił status na Zakończony'),

((SELECT id_uzytkownika FROM uzytkownicy WHERE email = 'admin@skysecure.pl'),
 '10.0.0.1', 'FLIGHT_STATUS_CHANGED', 'Lot SK1008 zmienił status na Odwołany');
