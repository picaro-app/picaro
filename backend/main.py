from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from pydantic import BaseModel
import models

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
# CREATE EVENT (Manual event_id)
# =========================
class EventCreate(BaseModel):
    event_id: str
    event_name: str
    photographer_id: int

@app.post("/create-event")
def create_event(data: EventCreate, db: Session = Depends(get_db)):

    existing_event = db.query(models.Event).filter(
        models.Event.event_id == data.event_id
    ).first()

    if existing_event:
        raise HTTPException(status_code=400, detail="Event ID already exists")

    new_event = models.Event(
        event_id=data.event_id,
        event_name=data.event_name,
        photographer_id=data.photographer_id
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return {
        "success": True,
        "event_id": new_event.event_id,
        "event_name": new_event.event_name
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
            for e from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from pydantic import BaseModel
import models

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
# CREATE EVENT (Manual event_id)
# =========================
class EventCreate(BaseModel):
    event_id: str
    event_name: str
    photographer_id: int

@app.post("/create-event")
def create_event(data: EventCreate, db: Session = Depends(get_db)):

    existing_event = db.query(models.Event).filter(
        models.Event.event_id == data.event_id
    ).first()

    if existing_event:
        raise HTTPException(status_code=400, detail="Event ID already exists")

    new_event = models.Event(
        event_id=data.event_id,
        event_name=data.event_name,
        photographer_id=data.photographer_id
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return {
        "success": True,
        "event_id": new_event.event_id,
        "event_name": new_event.event_name
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
