from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import routers.words as words
import routers.auth as auth
import routers.health as health
from models.base import Base

# Model importları (Base metadata için gerekli)
from models.user import User  # Eklendi
from models.word import Word  # Eklendi

# Sadece bu satırı kullanın:
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(words.router)
app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)