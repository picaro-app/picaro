from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
import models

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Picaro backend running 🚀"}


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

    return {"message": "Photographer account created successfully"}