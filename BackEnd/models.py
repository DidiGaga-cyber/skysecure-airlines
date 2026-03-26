from sqlalchemy import Column, Integer, String, TIMESTAMP, text, Numeric
from database import Base

class User(Base):
    __tablename__ = "Uzytkownicy" # PostgreSQL zamieni wielkie litery na małe, jeśli nie użyliśmy cudzysłowu w SQL

    id_uzytkownika = Column(Integer, primary_key=True, index=True)
    nazwisko = Column(String(50), nullable=False)
    imie = Column(String(30), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    haslo_hash = Column(String(255), nullable=False)
    rola = Column(String(20), server_default="User")
    data_rejestracji = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class Flight(Base):
    __tablename__ = "loty" # Название таблицы в БД

    id_lotu = Column(Integer, primary_key=True, index=True)
    numer_lotu = Column(String(10), unique=True, nullable=False)
    miejsce_wylotu = Column(String(100), nullable=False)
    miejsce_przylotu = Column(String(100), nullable=False)
    data_wylotu = Column(TIMESTAMP, nullable=False)
    cena = Column(Numeric(10, 2), nullable=False)
    wolne_miejsca = Column(Integer, default=150)