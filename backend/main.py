from fastapi import FastAPI
from database import engine, Base
import models

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Picaro backend running 🚀"}