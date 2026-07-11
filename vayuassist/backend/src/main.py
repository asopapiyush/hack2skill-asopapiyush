from dotenv import load_dotenv

# Load env variables FIRST
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, chat
from src.config.database import engine
from src.models.models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VayuAssist API",
    description="Monsoon Preparedness Assistant",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "VayuAssist API"}
