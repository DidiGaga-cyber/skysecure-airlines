from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from auth import router as auth_router
from flights import router as flights_router
from bookings import router as bookings_router
from tickets import router as tickets_router
from payments import router as payments_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkySecure Airlines API", root_path="/api")

origins = [
    "https://localhost",
    "https://127.0.0.1",
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)

api_router = APIRouter()

@api_router.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "database": "connected"}

app.include_router(api_router)
app.include_router(flights_router)
app.include_router(bookings_router)
app.include_router(tickets_router)
app.include_router(payments_router)
