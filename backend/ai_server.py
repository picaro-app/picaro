from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from deepface import DeepFace
import os
import shutil

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
# Upload base folder
# =========================
UPLOAD_FOLDER = "backend/uploads/events"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# Serve Static Files (CSS, JS)
# =========================
app.mount("/static", StaticFiles(directory="backend"), name="static")

# =========================
# UI Routes
# =========================

# Client UI
@app.get("/")
def serve_client():
    return FileResponse("backend/index.html")

# Photographer Login
@app.get("/photographer")
def serve_photographer():
    return FileResponse("backend/login.html")

# Dashboard
@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("backend/dashboard.html")

# Manage Page
@app.get("/manage")
def serve_manage():
    return FileResponse("backend/manage.html")

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

    temp_path = f"temp_{selfie.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(selfie.file, buffer)

    event_folder = os.path.join(UPLOAD_FOLDER, event_id)

    matched = match_faces(temp_path, event_folder)

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return {
        "success": True,
        "matched": matched
    }