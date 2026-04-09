from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

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
    czas_odlotu: datetime # Было data_wylotu
    czas_przylotu: datetime 
    cena: float
    liczba_miejsc: int # Было wolne_miejsca
    status: str

    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    id_lotu: int


## changed data_rezerwacji: datetime into data_utworzenia: datetime
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
    ## paszport: str # Убрано, так как паспортные данные больше не требуются для бронирования


class SeatOut(BaseModel):
    id_miejsca: int
    id_lotu: int
    numer_miejsca: str
    klasa: str
    czy_wolne: bool

    class Config:
        from_attributes = True