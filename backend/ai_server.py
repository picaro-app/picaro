from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from deepface import DeepFace
import cloudinary
import cloudinary.uploader
import os
import shutil
import uuid

# =========================
# DATABASE IMPORTS
# =========================
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
# Upload Folder (Temporary Local)
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
# PHOTOGRAPHER SIGNUP
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
# FACE MATCHING LOGIC
# =========================
def match_faces(selfie_path, event_folder):

    if not os.path.exists(event_folder):
        return []

    files = os.listdir(event_folder)
    matched = []

    for file in files:
        file_path = os.path.join(event_folder, file)

        if os.path.isdir(file_path):
            continue

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
        temp_filename = f"{uuid.uuid4()}_{selfie.filename}"
        temp_path = f"/tmp/{temp_filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(selfie.file, buffer)

        upload_result = cloudinary.uploader.upload(
            temp_path,
            folder=f"picaro_selfies/{event_id}"
        )

        selfie_url = upload_result["secure_url"]

        event_folder = os.path.join(UPLOAD_FOLDER, event_id)
        matched = match_faces(temp_path, event_folder)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "success": True,
            "selfie_url": selfie_url,
            "matched": matched
        }

    except Exception as e:
        print("MATCH ERROR:", e)
        return {
            "success": False,
            "error": "AI Server Error"
        }

# =========================
# STATIC FILES
# =========================
app.mount("/", StaticFiles(directory=".", html=True), name="static")