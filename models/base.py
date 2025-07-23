from datetime import datetime
from sqlalchemy import Column, DateTime
from database import Base # database.py dosyasındaki Base'i kullanıyoruz
from sqlalchemy.sql import func

# Tüm modellerin miras alacağı temel model
class BaseModel(Base):
    __abstract__ = True # Bu sınıf bir veritabanı tablosu olarak oluşturulmayacak

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())