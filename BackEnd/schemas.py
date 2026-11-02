from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    imie: str
    nazwisko: str

class UserOut(BaseModel):
    id_uzytkownika: int
    email: EmailStr
    imie: str
    rola: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class FlightOut(BaseModel):
    id_lotu: int
    numer_lotu: str
    id_lotniska_odlotu: int
    id_lotniska_przylotu: int
    czas_odlotu: datetime
    czas_przylotu: datetime 
    cena: float
    liczba_miejsc: int
    status: str

    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    id_lotu: int

class ReservationOut(BaseModel):
    id_rezerwacji: int
    id_uzytkownika: int
    id_lotu: int
    data_utworzenia: datetime
    status: str

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    id_rezerwacji: int
    id_miejsca: int
    imie: str
    nazwisko: str

class SeatOut(BaseModel):
    id_miejsca: int
    id_lotu: int
    numer_miejsca: str
    klasa: str
    czy_wolne: bool

    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    id_rezerwacji: int
    metoda: str

class PaymentOut(BaseModel):
    id_platnosci: int
    id_rezerwacji: int
    kwota: Decimal
    status_transakcji: str
    metoda: str
    identyfikator_sesji: Optional[UUID]

    class Config:
        from_attributes = True

class FlightCreate(BaseModel):
    numer_lotu: str
    id_lotniska_odlotu: int
    id_lotniska_przylotu: int
    czas_odlotu: datetime
    czas_przylotu: datetime
    cena: Decimal
    liczba_miejsc: int
    status: Optional[str] = "Zaplanowany"

class FlightUpdate(BaseModel):
    numer_lotu: Optional[str] = None
    id_lotniska_odlotu: Optional[int] = None
    id_lotniska_przylotu: Optional[int] = None
    czas_odlotu: Optional[datetime] = None
    czas_przylotu: Optional[datetime] = None
    cena: Optional[Decimal] = None
    liczba_miejsc: Optional[int] = None
    status: Optional[str] = None
