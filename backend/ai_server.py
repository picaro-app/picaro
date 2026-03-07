from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from deepface import DeepFace
import cloudinary
import cloudinary.uploader
import os
import shutil
import uuid
import fastapi import Form

from database import engine, Base, SessionLocal
import models

app = FastAPI()

# =========================
# CREATE TABLES
# =========================
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
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CLOUDINARY CONFIG
# =========================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# =========================
# UPLOAD FOLDER
# =========================
UPLOAD_FOLDER = "uploads/events"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}

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

    return {"success": True}

# =========================
# LOGIN
# =========================
@app.post("/login")
def login(email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):

    user = db.query(models.Photographer).filter(
        models.Photographer.email == email
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if user.password != password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {
        "success": True,
        "photographer_id": user.id,
        "name": user.name
    }

# =========================
# CREATE EVENT
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

    event_path = os.path.join(UPLOAD_FOLDER, data.event_id)
    os.makedirs(event_path, exist_ok=True)

    return {
        "success": True,
        "event_id": new_event.event_id
    }

# =========================
# GET EVENTS
# =========================
@app.get("/my-events/{photographer_id}")
def get_my_events(photographer_id: int, db: Session = Depends(get_db)):

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
# UPLOAD PHOTOS
# =========================
@app.post("/upload-photos")
async def upload_photos(
    event_id: str = Form(...),
    photographer_id: int = Body(...),
    photos: list[UploadFile] = File(...)
):

    try:

        event_folder = os.path.join(UPLOAD_FOLDER, event_id)
        os.makedirs(event_folder, exist_ok=True)

        uploaded = []

        for photo in photos:

            filename = f"{uuid.uuid4()}_{photo.filename}"
            file_path = os.path.join(event_folder, filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)

            result = cloudinary.uploader.upload(
                file_path,
                folder=f"picaro_events/{event_id}"
            )

            uploaded.append(result["secure_url"])

        return {
            "success": True,
            "uploaded": uploaded
        }

    except Exception as e:

        print("UPLOAD ERROR:", e)

        return {"success": False}

# =========================
# FACE MATCH
# =========================
def match_faces(selfie_path, event_folder):

    files = os.listdir(event_folder)
    matched = []

    for file in files:

        file_path = os.path.join(event_folder, file)

        try:

            result = DeepFace.verify(
                img1_path=selfie_path,
                img2_path=file_path,
                model_name="Facenet",
                enforce_detection=False
            )

            if result.get("verified"):
                matched.append(file)

        except Exception as e:

            print("Error verifying:", e)

    return matched


# =========================
# MATCH API
# =========================
@app.post("/match/{event_id}")
async def match(event_id: str, selfie: UploadFile = File(...)):

    try:

        temp_path = f"/tmp/{uuid.uuid4()}_{selfie.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(selfie.file, buffer)

        upload_result = cloudinary.uploader.upload(
            temp_path,
            folder=f"picaro_selfies/{event_id}"
        )

        selfie_url = upload_result["secure_url"]

        event_folder = os.path.join(UPLOAD_FOLDER, event_id)

        matched = match_faces(temp_path, event_folder)

        os.remove(temp_path)

        return {
            "success": True,
            "selfie_url": selfie_url,
            "matched": matched
        }

    except Exception as e:

        print("MATCH ERROR:", e)

        return {
            "success": False
        }

# =========================
# STATIC FILES
# =========================
app.mount("/", StaticFiles(directory=".", html=True), name="static")