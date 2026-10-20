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
                    ON CONFLICT (kod_iata) DO NOTHING;
                """)
                res = conn.execute(query, {
                    "kod_iata": str(row['kod_iata']).strip().upper()[:3],
                    "nazwa": str(row['nazwa']).strip()[:100],
                    "miasto": str(row['miasto']).strip()[:100],
                    "kraj": str(row['kraj']).strip()[:50]
                })
                if res.rowcount > 0:
                    inserted_count += 1
        logger.info(f"Импортировано новых аэропортов: {inserted_count}")
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
    """ Проверяет наличие аэропорта по IATA-коду. Если отсутствует — создаёт заглушку для целостности FK. """
    kod_iata = str(kod_iata).strip().upper()[:3]
    check_query = text("SELECT id_lotniska FROM lotniska WHERE kod_iata = :kod")
    res = conn.execute(check_query, {"kod": kod_iata}).fetchone()
    if res:
        return res[0]
    
    insert_query = text("""
        INSERT INTO lotniska (kod_iata, nazwa, miasto, kraj)
        VALUES (:kod, :nazwa, 'Unknown', 'Unknown')
        RETURNING id_lotniska;
    """)
    res = conn.execute(insert_query, {"kod": kod_iata, "nazwa": f"Lotnisko {kod_iata}"}).fetchone()
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