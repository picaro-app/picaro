from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from pydantic import BaseModel
import models
import os
from datetime import datetime
from typing import List

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# =========================
# DB Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"message": "Picaro backend running 🚀"}

# =========================
# DASHBOARD PAGE
# =========================
@app.get("/dashboard")
def dashboard():
    return FileResponse("dashboard.html")

# =========================
# SIGNUP
# =========================
@app.post("/signup")
def signup(name: str, email: str, password: str, db: Session = Depends(get_db)):

    existing_user = db.query(models.Photographer).filter(
        models.Photographer.email == email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.Photographer(
        name=name,
        email=email,
        password=password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "success": True,
        "message": "Photographer account created successfully"
    }

# =========================
# LOGIN
# =========================
class LoginData(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):

    user = db.query(models.Photographer).filter(
        models.Photographer.email == data.email
    ).first()

    if not user:
        return {"success": False}

    if user.password != data.password:
        return {"success": False}

    return {
        "success": True,
        "photographer_id": user.id,
        "name": user.name
    }

# =========================
# GET PHOTOGRAPHER EVENTS
# =========================
@app.get("/my-events/{photographer_id}")
def get_events(photographer_id: int, db: Session = Depends(get_db)):

    events = db.query(models.Event).filter(
        models.Event.photographer_id == photographer_id
    ).all()

    return {
        "success": True,
        "events": [
            {
                "event_id": e.event_id,
                "event_name": e.event_name,
                "created_at": e.created_at
            }
            for e in events
        ]
    }

# =========================
# UPLOAD PHOTOS + AUTO CREATE EVENT
# =========================
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.post("/upload-photos")
async def upload_photos(
    event_id: str = Form(...),
    photographer_id: int = Form(...),
    photos: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):

    # Check event
    event = db.query(models.Event).filter(
        models.Event.event_id == event_id
    ).first()

    # Auto create event
    if not event:
        event = models.Event(
            event_id=event_id,
            event_name=event_id,
            photographer_id=photographer_id,
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

    # Create folder
    event_folder = os.path.join("uploads", event_id)
    os.makedirs(event_folder, exist_ok=True)

    # Save files
    for photo in photos:
        file_location = os.path.join(event_folder, photo.filename)

        with open(file_location, "wb") as buffer:
            buffer.write(await photo.read())

    return {
        "success": True,
        "event_id": event_id,
        "uploaded": len(photos)
    }