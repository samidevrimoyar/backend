# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine # Base ve engine'i database.py'den içe aktarın
import routers.auth as auth # Kimlik doğrulama router'ını içe aktarın
import os # Ortam değişkenlerini okumak için

# BURAYI EKLEYİN: Yeni modelleri (word.py) içe aktarın ki Base.metadata.create_all bunları tanısın
import models.word
import models.user # User modelinin de burada içe aktarılması iyi pratiktir, emin olmak için

# Veritabanı tablolarını oluşturun
# Bu, modellerinizi tanımladıktan sonra çalışacaktır
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Superisi Dictionary API",
    description="A dictionary and user management API for Superisi.",
    version="0.0.1",
)

# CORS Ayarları (Geliştirme ortamında her yerden erişime izin verir)
# Üretim ortamında belirli origin'lere kısıtlamanız ÖNEMLİDİR.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tüm origin'lere izin ver
    allow_credentials=True,
    allow_methods=["*"], # Tüm HTTP metotlarına izin ver
    allow_headers=["*"], # Tüm başlıkları kabul et
)

# Health Check Endpoint
@app.get("/", summary="Root endpoint for API health check")
async def root():
    return {"message": "Welcome to Superisi Dictionary API! Visit /docs for API documentation."}

# Router'ları ekle
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


# BURAYI EKLEYİN: words router'ı (bir sonraki adımda oluşturacağız)
import routers.words as words # Henüz yok, sonra uncomment edeceğiz
app.include_router(words.router, prefix="/words", tags=["Dictionary"])

# Uygulama ayağa kalktığında çalışacak kod (isteğe bağlı)
@app.on_event("startup")
async def startup_event():
    print("FastAPI application started up.")
    # DEBUG modu kontrolü
    debug_mode = os.getenv("DEBUG", "0").lower() in ("true", "1")
    if debug_mode:
        print("Running in DEBUG mode.")

@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI application is shutting down.")