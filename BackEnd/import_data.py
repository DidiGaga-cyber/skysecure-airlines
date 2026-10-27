import os
import sys
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 1. Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CSV_Importer")

# 2. Подключение к БД (по умолчанию порт 5433 для локального запуска, 5432 для Docker)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://skysecure_user:skysecure_password@localhost:5433/skysecure_db"
)

# Словарь известных международных аэропортов (fallback)
KNOWN_AIRPORTS = {
    'ADD': ('Bole International Airport', 'Addis Ababa', 'Ethiopia'),
    'AKL': ('Auckland Airport', 'Auckland', 'New Zealand'),
    'AMS': ('Amsterdam Airport Schiphol', 'Amsterdam', 'Netherlands'),
    'ATL': ('Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'United States'),
    'BKK': ('Suvarnabhumi Airport', 'Bangkok', 'Thailand'),
    'BOG': ('El Dorado International Airport', 'Bogota', 'Colombia'),
    'BOM': ('Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'India'),
    'CAI': ('Cairo International Airport', 'Cairo', 'Egypt'),
    'CDG': ('Charles de Gaulle Airport', 'Paris', 'France'),
    'CPH': ('Copenhagen Airport', 'Copenhagen', 'Denmark'),
    'CPT': ('Cape Town International Airport', 'Cape Town', 'South Africa'),
    'DEL': ('Indira Gandhi International Airport', 'Delhi', 'India'),
    'DEN': ('Denver International Airport', 'Denver', 'United States'),
    'DFW': ('Dallas/Fort Worth International Airport', 'Dallas', 'United States'),
    'DOH': ('Hamad International Airport', 'Doha', 'Qatar'),
    'DXB': ('Dubai International Airport', 'Dubai', 'United Arab Emirates'),
    'EZE': ('Ministro Pistarini International Airport', 'Buenos Aires', 'Argentina'),
    'FCO': ('Leonardo da Vinci-Fiumicino Airport', 'Rome', 'Italy'),
    'FRA': ('Frankfurt am Main Airport', 'Frankfurt', 'Germany'),
    'GRU': ('Sao Paulo/Guarulhos International Airport', 'Sao Paulo', 'Brazil'),
    'HKG': ('Hong Kong International Airport', 'Hong Kong', 'Hong Kong'),
    'HND': ('Tokyo Haneda Airport', 'Tokyo', 'Japan'),
    'ICN': ('Incheon International Airport', 'Seoul', 'South Korea'),
    'JFK': ('John F. Kennedy International Airport', 'New York', 'United States'),
    'JNB': ('O.R. Tambo International Airport', 'Johannesburg', 'South Africa'),
    'LAX': ('Los Angeles International Airport', 'Los Angeles', 'United States'),
    'LHR': ('Heathrow Airport', 'London', 'United Kingdom'),
    'LUZ': ('Port Lotniczy Lublin', 'Lublin', 'Polska'),
    'MAD': ('Adolfo Suarez Madrid-Barajas Airport', 'Madrid', 'Spain'),
    'MEL': ('Melbourne Airport', 'Melbourne', 'Australia'),
    'MEX': ('Mexico City International Airport', 'Mexico City', 'Mexico'),
    'MIA': ('Miami International Airport', 'Miami', 'United States'),
    'MUC': ('Munich Airport', 'Munich', 'Germany'),
    'ORD': ("O'Hare International Airport", 'Chicago', 'United States'),
    'SCL': ('Arturo Merino Benitez International Airport', 'Santiago', 'Chile'),
    'SFO': ('San Francisco International Airport', 'San Francisco', 'United States'),
    'SIN': ('Singapore Changi Airport', 'Singapore', 'Singapore'),
    'SYD': ('Sydney Kingsford Smith Airport', 'Sydney', 'Australia'),
    'VIE': ('Vienna International Airport', 'Vienna', 'Austria'),
    'WAW': ('Lotnisko Chopina', 'Warszawa', 'Polska'),
    'YVR': ('Vancouver International Airport', 'Vancouver', 'Canada'),
    'YYZ': ('Toronto Pearson International Airport', 'Toronto', 'Canada'),
    'ZRH': ('Zurich Airport', 'Zurich', 'Switzerland'),
}

def get_engine():
    try:
        engine = create_engine(DATABASE_URL)
        logger.info(f"Подключение к БД успешно: {engine.url.host}:{engine.url.port}/{engine.url.database}")
        return engine
    except Exception as e:
        logger.error(f"Не удалось создать подключение к БД: {e}")
        sys.exit(1)

def import_lotniska(engine, csv_path="lotniska.csv"):
    logger.info(f"--- Чтение и импорт аэропортов: {csv_path} ---")
    try:
        df = pd.read_csv(csv_path)
        # Заполнение пропущенных значений в текстовых полях
        df['miasto'] = df['miasto'].fillna('Nieokreślone')
        df['kraj'] = df['kraj'].fillna('Nieokreślone')
        
        inserted_count = 0
        with engine.begin() as conn:
            for _, row in df.iterrows():
                query = text("""
                    INSERT INTO lotniska (kod_iata, nazwa, miasto, kraj)
                    VALUES (:kod_iata, :nazwa, :miasto, :kraj)
                    ON CONFLICT (kod_iata) DO UPDATE SET
                        nazwa = CASE WHEN lotniska.nazwa LIKE 'Lotnisko %' AND EXCLUDED.nazwa NOT LIKE 'Lotnisko %' THEN EXCLUDED.nazwa ELSE lotniska.nazwa END,
                        miasto = CASE WHEN lotniska.miasto IN ('Unknown', 'Nieokreślone', '') AND EXCLUDED.miasto NOT IN ('Unknown', 'Nieokreślone', '') THEN EXCLUDED.miasto ELSE lotniska.miasto END,
                        kraj = CASE WHEN lotniska.kraj IN ('Unknown', 'Nieokreślone', '') AND EXCLUDED.kraj NOT IN ('Unknown', 'Nieokreślone', '') THEN EXCLUDED.kraj ELSE lotniska.kraj END;
                """)
                res = conn.execute(query, {
                    "kod_iata": str(row['kod_iata']).strip().upper()[:3],
                    "nazwa": str(row['nazwa']).strip()[:100],
                    "miasto": str(row['miasto']).strip()[:100],
                    "kraj": str(row['kraj']).strip()[:50]
                })
                if res.rowcount > 0:
                    inserted_count += 1
        logger.info(f"Импортировано/обновлено аэропортов: {inserted_count}")
    except Exception as e:
        logger.error(f"Ошибка при импорте аэропортов: {e}")
        raise

def import_uzytkownicy(engine, csv_path="uzytkownicy.csv"):
    logger.info(f"--- Чтение и импорт пользователей: {csv_path} ---")
    try:
        df = pd.read_csv(csv_path)
        inserted_count = 0
        with engine.begin() as conn:
            for _, row in df.iterrows():
                query = text("""
                    INSERT INTO uzytkownicy (imie, nazwisko, email, haslo_hash, rola)
                    VALUES (:imie, :nazwisko, :email, :haslo_hash, :rola)
                    ON CONFLICT (email) DO NOTHING;
                """)
                res = conn.execute(query, {
                    "imie": str(row['imie']).strip()[:30],
                    "nazwisko": str(row['nazwisko']).strip()[:50],
                    "email": str(row['email']).strip().lower()[:100],
                    "haslo_hash": str(row['haslo_hash']).strip(),
                    "rola": str(row['rola']).strip() if 'rola' in row and pd.notna(row['rola']) else 'User'
                })
                if res.rowcount > 0:
                    inserted_count += 1
        logger.info(f"Импортировано новых пользователей: {inserted_count}")
    except Exception as e:
        logger.error(f"Ошибка при импорте пользователей: {e}")
        raise

def ensure_airport_exists(conn, kod_iata):
    """ Проверяет наличие аэропорта по IATA-коду. Если отсутствует — создаёт с известными данными или заглушкой. """
    kod_iata = str(kod_iata).strip().upper()[:3]
    check_query = text("SELECT id_lotniska, miasto FROM lotniska WHERE kod_iata = :kod")
    res = conn.execute(check_query, {"kod": kod_iata}).fetchone()
    
    if res:
        # Если аэропорт был создан как Unknown, но у нас есть данные в KNOWN_AIRPORTS, обновляем его
        if res[1] in ("Unknown", "Nieokreślone", "") and kod_iata in KNOWN_AIRPORTS:
            nazwa, miasto, kraj = KNOWN_AIRPORTS[kod_iata]
            conn.execute(text("""
                UPDATE lotniska SET nazwa = :nazwa, miasto = :miasto, kraj = :kraj
                WHERE id_lotniska = :id
            """), {"nazwa": nazwa, "miasto": miasto, "kraj": kraj, "id": res[0]})
        return res[0]
    
    if kod_iata in KNOWN_AIRPORTS:
        nazwa, miasto, kraj = KNOWN_AIRPORTS[kod_iata]
    else:
        nazwa, miasto, kraj = f"Lotnisko {kod_iata}", "Unknown", "Unknown"

    insert_query = text("""
        INSERT INTO lotniska (kod_iata, nazwa, miasto, kraj)
        VALUES (:kod, :nazwa, :miasto, :kraj)
        RETURNING id_lotniska;
    """)
    res = conn.execute(insert_query, {
        "kod": kod_iata,
        "nazwa": nazwa,
        "miasto": miasto,
        "kraj": kraj
    }).fetchone()
    return res[0]

def import_loty(engine, csv_path="loty.csv"):
    logger.info(f"--- Чтение и импорт рейсов: {csv_path} ---")
    try:
        df = pd.read_csv(csv_path)
        
        # Конвертация дат в формат Timestamp
        df['departure_time_dt'] = pd.to_datetime(df['departure_time'], errors='coerce')
        df['arrival_time_dt'] = pd.to_datetime(df['arrival_time'], errors='coerce')
        
        inserted_count = 0
        with engine.begin() as conn:
            for _, row in df.iterrows():
                if pd.isna(row['departure_time_dt']) or pd.isna(row['arrival_time_dt']):
                    logger.warning(f"Пропуск рейса {row.get('flight_number')}: некорректная дата")
                    continue
                
                # Получение ID аэропортов вылета и прилета
                id_dep = ensure_airport_exists(conn, row['departure_airport_code'])
                id_arr = ensure_airport_exists(conn, row['arrival_airport_code'])
                
                flight_num = str(row['flight_number']).strip()[:10]
                status_val = str(row['status']).strip() if 'status' in row and pd.notna(row['status']) else 'Zaplanowany'
                
                query = text("""
                    INSERT INTO loty (
                        numer_lotu, id_lotniska_odlotu, id_lotniska_przylotu,
                        czas_odlotu, czas_przylotu, cena, liczba_miejsc, status
                    )
                    VALUES (
                        :numer_lotu, :id_dep, :id_arr,
                        :czas_odlotu, :czas_przylotu, :cena, :liczba_miejsc, :status
                    )
                    ON CONFLICT (numer_lotu) DO NOTHING;
                """)
                
                res = conn.execute(query, {
                    "numer_lotu": flight_num,
                    "id_dep": id_dep,
                    "id_arr": id_arr,
                    "czas_odlotu": row['departure_time_dt'].to_pydatetime(),
                    "czas_przylotu": row['arrival_time_dt'].to_pydatetime(),
                    "cena": float(row['price']),
                    "liczba_miejsc": int(row['seats_available']),
                    "status": status_val
                })
                
                if res.rowcount > 0:
                    inserted_count += 1
                    
        logger.info(f"Импортировано новых рейсов: {inserted_count}")
    except Exception as e:
        logger.error(f"Ошибка при импорте рейсов: {e}")
        raise

def main():
    logger.info("=== Старт импорта CSV-данных ===")
    engine = get_engine()
    
    try:
        # Порядок импорта важен из-за связей Foreign Key!
        import_lotniska(engine, "lotniska.csv")
        import_uzytkownicy(engine, "uzytkownicy.csv")
        import_loty(engine, "loty.csv")
        logger.info("=== Импорт успешно завершён ===")
    except Exception as e:
        logger.critical(f"Критическая ошибка процесса импорта: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
