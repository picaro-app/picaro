from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from deepface import DeepFace
import cloudinary
import cloudinary.uploader
import os
import shutil
import uuid

app = FastAPI()

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
# Health Check
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# Face Matching Logic
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
# Match API
# =========================
@app.post("/match/{event_id}")
async def match(event_id: str, selfie: UploadFile = File(...)):

    try:
        # Unique temp filename
        temp_filename = f"{uuid.uuid4()}_{selfie.filename}"
        temp_path = f"/tmp/{temp_filename}"

        # Save selfie locally
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(selfie.file, buffer)

        # Upload selfie to Cloudinary
        upload_result = cloudinary.uploader.upload(
            temp_path,
            folder=f"picaro_selfies/{event_id}"
        )

        selfie_url = upload_result["secure_url"]

        # Local folder matching (temporary logic)
        event_folder = os.path.join(UPLOAD_FOLDER, event_id)
        matched = match_faces(temp_path, event_folder)

        # Remove temp file
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