from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from minio import Minio
from minio.error import S3Error
import os
import time
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

def check_database(db: Session):
    try:
        db.execute("SELECT 1")
        return True
    except Exception:
        return False

def check_minio():
    try:
        minio_client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=False
        )
        minio_client.list_buckets()
        return True
    except S3Error:
        return False

@router.get("/") # Bu satırı ekleyin veya mevcutsa kontrol edin
async def read_root():
    return {"message": "Welcome to the Superisi API!"}

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = check_database(db)
    minio_status = check_minio()

    status_code = 200 if db_status and minio_status else 503

    response = {
        "status": "OK" if status_code == 200 else "SERVICE_UNAVAILABLE",
        "version": "1.0.0",
        "dependencies": {
            "database": {
                "status": "OK" if db_status else "DOWN",
                "details": "PostgreSQL connection"
            },
            "object_storage": {
                "status": "OK" if minio_status else "DOWN",
                "details": "MinIO connection"
            }
        }
    }

    return JSONResponse(content=response, status_code=status_code)