from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
import models, schemas
from database import get_db

router = APIRouter(prefix="/api/flights", tags=["flights"])

@router.get("/", response_model=List[schemas.FlightOut])
def get_flights(
    origin: Optional[str] = Query(None, alias="from"),
    destination: Optional[str] = Query(None, alias="to"),
    departure_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Flight)

    if origin:
        query = query.filter(models.Flight.miejsce_wylotu.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(models.Flight.miejsce_przylotu.ilike(f"%{destination}%"))
    if departure_date:
        # Фильтруем только по дате (без учета времени)
        query = query.filter(func.date(models.Flight.data_wylotu) == departure_date)

    return query.all()