from sqlalchemy import Column, Integer, String, TIMESTAMP, text, Numeric, ForeignKey, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class User(Base):
    __tablename__ = "Uzytkownicy"

    id_uzytkownika = Column(Integer, primary_key=True, index=True)
    nazwisko = Column(String(50), nullable=False)
    imie = Column(String(30), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    haslo_hash = Column(String(255), nullable=False)
    rola = Column(String(20), server_default="User")
##    data_rejestracji = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relacje
    rezerwacje = relationship("Rezerwacja", back_populates="uzytkownik", cascade="all, delete")
    logi = relationship("LogAudytowy", back_populates="uzytkownik")

class Airport(Base):
    __tablename__ = "Lotniska"

    id_lotniska = Column(Integer, primary_key=True, index=True)
    kod_iata = Column(String(3), unique=True, nullable=False)
    nazwa = Column(String(100), nullable=False)
    miasto = Column(String(100), nullable=False)
    kraj = Column(String(50), nullable=False)

    loty_odloty = relationship("Flight", foreign_keys="[Flight.id_lotniska_odlotu]", back_populates="lotnisko_odlotu")
    loty_przyloty = relationship("Flight", foreign_keys="[Flight.id_lotniska_przylotu]", back_populates="lotnisko_przylotu")

class Flight(Base):
    __tablename__ = "Loty"

    id_lotu = Column(Integer, primary_key=True, index=True)
    numer_lotu = Column(String(10), unique=True, nullable=False)
    id_lotniska_odlotu = Column(Integer, ForeignKey("Lotniska.id_lotniska", ondelete="CASCADE"), nullable=False)
    id_lotniska_przylotu = Column(Integer, ForeignKey("Lotniska.id_lotniska", ondelete="CASCADE"), nullable=False)
    czas_odlotu = Column(TIMESTAMP, nullable=False)
    czas_przylotu = Column(TIMESTAMP, nullable=False)
    cena = Column(Numeric(10, 2), nullable=False)
    liczba_miejsc = Column(Integer, nullable=False)
    status = Column(String(20), server_default="Zaplanowany")

    # Relacje
    lotnisko_odlotu = relationship("Airport", foreign_keys=[id_lotniska_odlotu], back_populates="loty_odloty")
    lotnisko_przylotu = relationship("Airport", foreign_keys=[id_lotniska_przylotu], back_populates="loty_przyloty")
    miejsca = relationship("Miejsce", back_populates="lot", cascade="all, delete")
    rezerwacje = relationship("Rezerwacja", back_populates="lot", cascade="all, delete")

class Miejsce(Base):
    __tablename__ = "Miejsca"

    id_miejsca = Column(Integer, primary_key=True, index=True)
    id_lotu = Column(Integer, ForeignKey("Loty.id_lotu", ondelete="CASCADE"), nullable=False)
    numer_miejsca = Column(String(5), nullable=False)
    klasa = Column(String(20), server_default="Economy")
    czy_wolne = Column(Boolean, server_default=text("true"))

    lot = relationship("Flight", back_populates="miejsca")
    bilet = relationship("Bilet", back_populates="miejsce", uselist=False)

class Rezerwacja(Base):
    __tablename__ = "Rezerwacje"

    id_rezerwacji = Column(Integer, primary_key=True, index=True)
    id_uzytkownika = Column(Integer, ForeignKey("Uzytkownicy.id_uzytkownika", ondelete="CASCADE"), nullable=False)
    id_lotu = Column(Integer, ForeignKey("Loty.id_lotu", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), server_default="Oczekująca")
    kwota_laczna = Column(Numeric(10, 2), nullable=False)
    data_utworzenia = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    uzytkownik = relationship("User", back_populates="rezerwacje")
    lot = relationship("Flight", back_populates="rezerwacje")
    bilety = relationship("Bilet", back_populates="rezerwacja", cascade="all, delete")
    platnosci = relationship("Platnosc", back_populates="rezerwacja", cascade="all, delete")

class Bilet(Base):
    __tablename__ = "Bilety"

    id_biletu = Column(Integer, primary_key=True, index=True)
    id_rezerwacji = Column(Integer, ForeignKey("Rezerwacje.id_rezerwacji", ondelete="CASCADE"), nullable=False)
    id_miejsca = Column(Integer, ForeignKey("Miejsca.id_miejsca", ondelete="RESTRICT"), unique=True, nullable=False)
    imie_pasazera = Column(String(50), nullable=False)
    nazwisko_pasazera = Column(String(50), nullable=False)
    dane_paszportowe = Column(LargeBinary)

    rezerwacja = relationship("Rezerwacja", back_populates="bilety")
    miejsce = relationship("Miejsce", back_populates="bilet")

class Platnosc(Base):
    __tablename__ = "Platnosci"

    id_platnosci = Column(Integer, primary_key=True, index=True)
    id_rezerwacji = Column(Integer, ForeignKey("Rezerwacje.id_rezerwacji", ondelete="CASCADE"), nullable=False)
    kwota = Column(Numeric(10, 2), nullable=False)
    status_transakcji = Column(String(20), server_default="Pending")
    metoda = Column(String(50), nullable=False)
    data_transakcji = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    identyfikator_sesji = Column(UUID(as_uuid=True))

    rezerwacja = relationship("Rezerwacja", back_populates="platnosci")

class LogAudytowy(Base):
    __tablename__ = "Logi_Audytowe"

    id_logu = Column(Integer, primary_key=True, index=True)
    id_uzytkownika = Column(Integer, ForeignKey("Uzytkownicy.id_uzytkownika", ondelete="SET NULL"))
    adres_ip = Column(String(45))
    akcja = Column(String(100), nullable=False)
    szczegoly = Column(String)
    data_zdarzenia = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    uzytkownik = relationship("User", back_populates="logi")