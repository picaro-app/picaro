from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import os
import shutil

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "backend/uploads/events"


# ===============================
# FACE MATCH FUNCTION (FINAL)
# ===============================
def match_faces(selfie_path, event_folder):

    print("\n======== DEBUG START ========")
    print("SELFIE PATH:", selfie_path)
    print("EVENT FOLDER:", event_folder)

    if not os.path.exists(event_folder):
        print("FOLDER NOT FOUND")
        return []

    files = os.listdir(event_folder)
    print("FILES FOUND:", files)

    # Load selfie
    selfie_image = face_recognition.load_image_file(selfie_path)
    selfie_encodings = face_recognition.face_encodings(selfie_image)

    if len(selfie_encodings) == 0:
        print("NO FACE FOUND IN SELFIE")
        return []

    selfie_encoding = selfie_encodings[0]

    matched_images = []
    seen = set()   # prevents duplicates


    # Check every file
    for file in files:

        file_path = os.path.join(event_folder, file)

        # Skip folders
        if os.path.isdir(file_path):
            continue

        print("\nCHECKING:", file_path)

        try:
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) == 0:
                print("NO FACE FOUND")
                continue

            best_distance = 1.0

            # Check ALL faces in image
            for encoding in encodings:

                distance = face_recognition.face_distance(
                    [selfie_encoding],
                    encoding
                )[0]

                print("FACE DISTANCE:", distance)

                if distance < best_distance:
                    best_distance = distance


            print("BEST DISTANCE:", best_distance)


            # STRICT MATCH CONDITION
            if best_distance < 0.50:

                if file not in seen:

                    print("MATCH CONFIRMED:", file)

                    matched_images.append(file)

                    seen.add(file)

            else:

                print("NOT MATCH")


        except Exception as e:
            print("ERROR:", e)


    print("\nMATCHED FILES:", matched_images)
    print("======== DEBUG END ========\n")

    return matched_images



# ===============================
# API ENDPOINT
# ===============================
@app.post("/match/{event_id}")
async def match(event_id: str, selfie: UploadFile = File(...)):

    print("\nAPI CALLED FOR EVENT:", event_id)

    temp_path = f"temp_{selfie.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(selfie.file, buffer)

    event_folder = os.path.join(UPLOAD_FOLDER, event_id)

    matched = match_faces(temp_path, event_folder)

    # Delete temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    image_urls = [
        f"http://localhost:5000/events/{event_id}/{img}"
        for img in matched
    ]

    print("RETURNING URLS:", image_urls)

    return {
        "success": True,
        "matched": image_urls
    }