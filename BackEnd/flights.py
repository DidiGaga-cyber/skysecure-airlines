from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/flights", tags=["flights"])

@router.get("/", response_model=List[schemas.FlightOut])
def get_flights(
    origin: Optional[str] = Query(None, alias="from", description="City or IATA code of departure"),
    destination: Optional[str] = Query(None, alias="to", description="City or IATA code of arrival"),
    departure_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import aliased
    
    AirportOrigin = aliased(models.Airport)
    AirportDest = aliased(models.Airport)

    query = db.query(models.Flight).join(
        AirportOrigin, models.Flight.id_lotniska_odlotu == AirportOrigin.id_lotniska
    ).join(
        AirportDest, models.Flight.id_lotniska_przylotu == AirportDest.id_lotniska
    )

    if origin:
        query = query.filter(
            (AirportOrigin.miasto.ilike(f"%{origin}%")) | 
            (AirportOrigin.kod_iata.ilike(f"{origin}"))
        )
    
    if destination:
        query = query.filter(
            (AirportDest.miasto.ilike(f"%{destination}%")) | 
            (AirportDest.kod_iata.ilike(f"{destination}"))
        )
        
    if departure_date:
        query = query.filter(func.date(models.Flight.czas_odlotu) == departure_date)

    return query.all()

@router.get("/{id_lotu}/seats", response_model=List[schemas.SeatOut])
def get_flight_seats(id_lotu: int, db: Session = Depends(get_db)):
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony")

    seats = db.query(models.Miejsce).filter(models.Miejsce.id_lotu == id_lotu).order_by(models.Miejsce.id_miejsca).all()
    if not seats:
        return []

    return seats

def generate_seats(flight_id: int, liczba_miejsc: int, db: Session) -> None:
    existing_seats = {
        s.numer_miejsca
        for s in db.query(models.Miejsce.numer_miejsca).filter(models.Miejsce.id_lotu == flight_id).all()
    }
    seats_needed = liczba_miejsc - len(existing_seats)
    if seats_needed <= 0:
        return

    COLUMNS = ["A", "B", "C", "D", "E", "F"]
    BUSINESS_ROWS = 2

    seats_to_insert = []
    row = 1
    while len(seats_to_insert) < seats_needed:
        for col in COLUMNS:
            if len(seats_to_insert) >= seats_needed:
                break
            seat_num = f"{row}{col}"
            if seat_num in existing_seats:
                continue
            klasa = "Business" if row <= BUSINESS_ROWS else "Economy"
            seats_to_insert.append(
                models.Miejsce(
                    id_lotu=flight_id,
                    numer_miejsca=seat_num,
                    klasa=klasa,
                    czy_wolne=True,
                )
            )
        row += 1

    db.bulk_save_objects(seats_to_insert)

def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.rola != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień. Wymagana rola: Admin.",
        )
    return current_user

@router.post("/", response_model=schemas.FlightOut, status_code=status.HTTP_201_CREATED)
def create_flight(
    flight_data: schemas.FlightCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    if not db.query(models.Airport).filter(models.Airport.id_lotniska == flight_data.id_lotniska_odlotu).first():
        raise HTTPException(status_code=404, detail=f"Lotnisko odlotu (id={flight_data.id_lotniska_odlotu}) nie istnieje.")
    if not db.query(models.Airport).filter(models.Airport.id_lotniska == flight_data.id_lotniska_przylotu).first():
        raise HTTPException(status_code=404, detail=f"Lotnisko przylotu (id={flight_data.id_lotniska_przylotu}) nie istnieje.")

    if flight_data.czas_przylotu <= flight_data.czas_odlotu:
        raise HTTPException(status_code=400, detail="Czas przylotu musi być późniejszy niż czas odlotu.")

    if db.query(models.Flight).filter(models.Flight.numer_lotu == flight_data.numer_lotu).first():
        raise HTTPException(status_code=409, detail=f"Lot o numerze '{flight_data.numer_lotu}' już istnieje.")

    new_flight = models.Flight(**flight_data.model_dump())
    db.add(new_flight)
    db.flush()

    generate_seats(new_flight.id_lotu, flight_data.liczba_miejsc, db)

    db.commit()
    db.refresh(new_flight)
    return new_flight

@router.put("/{id_lotu}", response_model=schemas.FlightOut)
def update_flight(
    id_lotu: int,
    flight_data: schemas.FlightUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony.")

    update_dict = flight_data.model_dump(exclude_unset=True)

    if "id_lotniska_odlotu" in update_dict:
        if not db.query(models.Airport).filter(models.Airport.id_lotniska == update_dict["id_lotniska_odlotu"]).first():
            raise HTTPException(status_code=404, detail="Nowe lotnisko odlotu nie istnieje.")
    if "id_lotniska_przylotu" in update_dict:
        if not db.query(models.Airport).filter(models.Airport.id_lotniska == update_dict["id_lotniska_przylotu"]).first():
            raise HTTPException(status_code=404, detail="Nowe lotnisko przylotu nie istnieje.")

    new_odlot = update_dict.get("czas_odlotu", flight.czas_odlotu)
    new_przylot = update_dict.get("czas_przylotu", flight.czas_przylotu)
    if new_przylot <= new_odlot:
        raise HTTPException(status_code=400, detail="Czas przylotu musi być późniejszy niż czas odlotu.")

    if "liczba_miejsc" in update_dict and update_dict["liczba_miejsc"] != flight.liczba_miejsc:
        new_count = update_dict["liczba_miejsc"]
        occupied = db.query(models.Miejsce).filter(
            models.Miejsce.id_lotu == id_lotu,
            models.Miejsce.czy_wolne == False
        ).count()
        if new_count < occupied:
            raise HTTPException(
                status_code=409,
                detail=f"Nie można zmniejszyć liczby miejsc poniżej {occupied} (zajętych)."
            )
        booked_seat_ids = db.query(models.Bilet.id_miejsca).join(
            models.Miejsce, models.Bilet.id_miejsca == models.Miejsce.id_miejsca
        ).filter(models.Miejsce.id_lotu == id_lotu)
        db.query(models.Miejsce).filter(
            models.Miejsce.id_lotu == id_lotu,
            models.Miejsce.czy_wolne == True,
            ~models.Miejsce.id_miejsca.in_(booked_seat_ids)
        ).delete(synchronize_session=False)
        db.flush()
        generate_seats(id_lotu, new_count, db)

    for field, value in update_dict.items():
        setattr(flight, field, value)

    db.commit()
    db.refresh(flight)
    return flight

@router.delete("/{id_lotu}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flight(
    id_lotu: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    flight = db.query(models.Flight).filter(models.Flight.id_lotu == id_lotu).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Lot nie znaleziony.")

    if flight.status == "W trakcie":
        raise HTTPException(
            status_code=409,
            detail="Nie można usunąć lotu w trakcie realizacji. Najpierw zmień status.",
        )

    db.query(models.Rezerwacja).filter(models.Rezerwacja.id_lotu == id_lotu).delete(synchronize_session=False)
    db.query(models.Flight).filter(models.Flight.id_lotu == id_lotu).delete(synchronize_session=False)
    db.commit()

@router.get("/airports/{id_lotniska}", tags=["airports"])
def get_airport(id_lotniska: int, db: Session = Depends(get_db)):
    airport = db.query(models.Airport).filter(models.Airport.id_lotniska == id_lotniska).first()
    if not airport:
        raise HTTPException(status_code=404, detail=f"Lotnisko o ID={id_lotniska} nie istnieje.")
    return {
        "id_lotniska": airport.id_lotniska,
        "kod_iata":    airport.kod_iata,
        "nazwa":       airport.nazwa,
        "miasto":      airport.miasto,
        "kraj":        airport.kraj,
    }
