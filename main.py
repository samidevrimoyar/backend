from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
import routers.words as words
import routers.auth as auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth.router)
app.include_router(words.router)

# Sağlık Kontrolü Endpoint'i
@app.get("/health/")
async def health_check(db: Session = Depends(get_db)):
    # PostgreSQL kontrolü
    try:
        db.execute("SELECT 1")
        db_status = "OK"
    except Exception:
        db_status = "ERROR"

    # MinIO kontrolü
    try:
        minio_client.list_buckets()
        minio_status = "OK"
    except S3Error:
        minio_status = "ERROR"

    return {
        "status": "SERVING" if db_status == "OK" and minio_status == "OK" else "FAILED",
        "postgresql": db_status,
        "minio": minio_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)