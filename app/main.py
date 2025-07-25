from fastapi import FastAPI, Depends
from .routers import auth, users, dictionary
from .database import engine, Base
from .dependencies import get_current_active_user

# Tablaları oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sözlük API",
    description="Kullanıcı tabanlı sözlük uygulaması",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Router'ları ekle
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api/users")
app.include_router(dictionary.router, prefix="/api/dictionary")

@app.get("/")
def read_root():
    return {"message": "Sözlük API'ye Hoş Geldiniz!"}

@app.get("/secure/", dependencies=[Depends(get_current_active_user)])
def secure_endpoint():
    return {"message": "Güvenli erişim başarılı"}