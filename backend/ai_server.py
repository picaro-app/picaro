from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
import os
import shutil

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload base folder
UPLOAD_FOLDER = "backend/uploads/events"

# Ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ✅ Root route (Railway health check friendly)
@app.get("/")
def root():
    return {"message": "Picaro backend is live 🚀"}


# ✅ Health route
@app.get("/health")
def health():
    return {"status": "ok"}


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