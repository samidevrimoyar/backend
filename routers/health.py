from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from minio import Minio
from minio.error import S3Error
import os
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

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    status = {
        "status": "OK",
        "services": {
            "database": "OK" if check_database(db) else "DOWN",
            "minio": "OK" if check_minio() else "DOWN"
        }
    }

    # Tüm servisler sağlıklı mı?
    if all(status == "OK" for status in status["services"].values()):
        return status
    else:
        return status  # İsterseniz burada 503 dönebilirsiniz