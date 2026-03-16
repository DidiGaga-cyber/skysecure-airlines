from sqlalchemy import Column, Integer, String, TIMESTAMP, text
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