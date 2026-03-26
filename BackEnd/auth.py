from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, auth_utils
from database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email już zajęty")
    
    new_user = models.User(
        email=user.email,
        imie=user.imie,
        nazwisko=user.nazwisko,
        haslo_hash=auth_utils.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)): # Używamy prostego modelu dla testu
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not auth_utils.verify_password(user_data.password, user.haslo_hash):
        raise HTTPException(status_code=401, detail="Błędne dane logowania")
    
    token = auth_utils.create_access_token(data={"sub": user.email, "role": user.rola})
    return {"access_token": token, "token_type": "bearer"}