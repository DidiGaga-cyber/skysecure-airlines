from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # Добавили стандарт OAuth2
import models, schemas, auth_utils
from database import get_db
from jose import JWTError, jwt
from auth_utils import SECRET_KEY, ALGORITHM


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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # В стандарте OAuth2 поле логина всегда называется "username", 
    # но мы передаем в него наш email.
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not auth_utils.verify_password(form_data.password, user.haslo_hash):
        raise HTTPException(status_code=401, detail="Błędne dane logowania")
    
    token = auth_utils.create_access_token(data={"sub": user.email, "role": user.rola})
    return {"access_token": token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен (в auth/login мы передавали 'sub': user.email)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    
    db.execute(text("SET LOCAL app.current_user_id = :uid"), {"uid": user.id_uzytkownika})
    db.execute(text("SET LOCAL app.current_user_role = :role"), {"role": user.rola})
    
    db_role = "app_admin_role" if user.rola == "Admin" else "app_user_role"
    db.execute(text(f"SET LOCAL ROLE {db_role}"))

    return user
