from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import os
import shutil

app = FastAPI()

# =========================
# CORS (ALLOW ALL)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# SAFE PATH FOR RAILWAY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "events")

# Ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# ROOT TEST ENDPOINT
# =========================
@app.get("/")
def root():
    return {"status": "PICARO AI RUNNING"}


# =========================
# FACE MATCH FUNCTION
# =========================
def match_faces(selfie_path, event_folder):

    print("\n======== DEBUG START ========")
    print("SELFIE PATH:", selfie_path)
    print("EVENT FOLDER:", event_folder)

    if not os.path.exists(event_folder):
        print("EVENT FOLDER NOT FOUND")
        return []

    files = os.listdir(event_folder)
    print("FILES:", files)

    selfie_image = face_recognition.load_image_file(selfie_path)
    selfie_encodings = face_recognition.face_encodings(selfie_image)

    if len(selfie_encodings) == 0:
        print("NO FACE IN SELFIE")
        return []

    selfie_encoding = selfie_encodings[0]

    matched_images = []
    seen = set()

    for file in files:

        file_path = os.path.join(event_folder, file)

        if os.path.isdir(file_path):
            continue

        try:

            print("CHECKING:", file)

            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) == 0:
                continue

            best_distance = 1.0

            for encoding in encodings:

                distance = face_recognition.face_distance(
                    [selfie_encoding],
                    encoding
                )[0]

                if distance < best_distance:
                    best_distance = distance

            print("DISTANCE:", best_distance)

            if best_distance < 0.50 and file not in seen:

                matched_images.append(file)
                seen.add(file)

                print("MATCH:", file)

        except Exception as e:
            print("ERROR:", e)

    print("MATCHED:", matched_images)
    print("======== DEBUG END ========\n")

    return matched_images


# =========================
# MATCH API
# =========================
@app.post("/match/{event_id}")
async def match(event_id: str, selfie: UploadFile = File(...)):

    print("API CALLED EVENT:", event_id)

    temp_path = os.path.join(BASE_DIR, f"temp_{selfie.filename}")

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(selfie.file, buffer)

    event_folder = os.path.join(UPLOAD_FOLDER, event_id)

    matched = match_faces(temp_path, event_folder)

    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Railway URL auto detect
    BASE_URL = os.environ.get("RAILWAY_STATIC_URL", "")

    image_urls = [
        f"{BASE_URL}/events/{event_id}/{img}"
        for img in matched
    ]

    return {
        "success": True,
        "matched": image_urls
    }