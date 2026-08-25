from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import auth, courses, sandbox, community, notes, user, coupons
import models
import time
import os
from sqlalchemy.exc import OperationalError
from initial_data import init_db

def create_tables():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully")
            break
        except OperationalError:
            print("Database not ready, retrying in 2 seconds...")
            time.sleep(2)
            retries -= 1

app = FastAPI(title="ProgLearn API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(sandbox.router)
app.include_router(community.router)
app.include_router(notes.router)
app.include_router(user.router)
app.include_router(coupons.router)

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

@app.on_event("startup")
def on_startup():
    create_tables()
    init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to ProgLearn API"}
