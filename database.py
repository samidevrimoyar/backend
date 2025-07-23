from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env dosyasını yükle (eğer Docker dışında çalıştırılıyorsa gerekli)
load_dotenv()

# Ortam değişkenlerinden veritabanı bağlantı bilgilerini al
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable not set.")

# SQLAlchemy motorunu oluştur
# echo=True, SQL sorgularını konsola yazdırır (geliştirme için faydalı)
engine = create_engine(DATABASE_URL, echo=os.getenv("DEBUG") == "1")

# Veritabanı oturum sınıfını oluştur
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM modelleri için temel sınıfı oluştur
Base = declarative_base()

# Bağımlılık Enjeksiyonu için veritabanı oturumu sağlayan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()