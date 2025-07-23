from datetime import datetime
from sqlalchemy import Column, DateTime
from database import Base # database.py dosyasındaki Base'i kullanıyoruz

# Tüm modellerin miras alacağı temel model
class BaseModel(Base):
    __abstract__ = True # Bu sınıf bir veritabanı tablosu olarak oluşturulmayacak

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)