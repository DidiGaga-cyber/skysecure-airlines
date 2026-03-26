from sqlalchemy import Column, Integer, String, TIMESTAMP, text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
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

class Airport(Base):
    """Model odpowiadający tabeli Lotniska"""
    __tablename__ = "lotniska"

    id_lotniska = Column(Integer, primary_key=True, index=True)
    kod_iata = Column(String(3), unique=True, nullable=False)
    nazwa = Column(String(100), nullable=False)
    miasto = Column(String(100), nullable=False)
    kraj = Column(String(50), nullable=False)

class Flight(Base):
    """Model odpowiadający tabeli Loty"""
    __tablename__ = "loty"

    id_lotu = Column(Integer, primary_key=True, index=True)
    numer_lotu = Column(String(10), unique=True, nullable=False)
    
    # Klucze obce wskazujące na ID lotniska w tabeli lotniska
    id_lotniska_odlotu = Column(Integer, ForeignKey("lotniska.id_lotniska", ondelete="CASCADE"), nullable=False)
    id_lotniska_przylotu = Column(Integer, ForeignKey("lotniska.id_lotniska", ondelete="CASCADE"), nullable=False)
    
    # Zgodność nazw z SQL: czas_odlotu i czas_przylotu
    czas_odlotu = Column(TIMESTAMP, nullable=False)
    czas_przylotu = Column(TIMESTAMP, nullable=False)
    
    cena = Column(Numeric(10, 2), nullable=False)
    liczba_miejsc = Column(Integer, nullable=False)
    status = Column(String(20), server_default="Zaplanowany")

    # Relacje (ułatwiają życie w SQLAlchemy)
    odlot_z = relationship("Airport", foreign_keys=[id_lotniska_odlotu])
    przylot_do = relationship("Airport", foreign_keys=[id_lotniska_przylotu])