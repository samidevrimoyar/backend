from fastapi import APIRouter, Depends, HTTPException, status, Form # 'Form'u ekledik
from fastapi.security import OAuth2PasswordBearer # OAuth2 (JWT) için
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models.user import User # User modelini içe aktarın
from passlib.context import CryptContext
from jose import JWTError, jwt # python-jose kütüphanesinden içe aktarın
from datetime import datetime, timedelta
import os # Ortam değişkenlerini okumak için
from typing import Optional # 'Optional' tipi için gerekli

router = APIRouter()

# Şifre hashleme için CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ortam değişkeninden gizli anahtarı al
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise Exception("SECRET_KEY environment variable not set.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 şifre taşıyıcısı (Bearer token)
# Swagger UI'ın "Authorize" penceresinde kullanıcı adı/şifre alanlarını göstermesi için tokenUrl gerekli.
# URL'in başında "/" olduğundan emin olun.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Şifre doğrulama fonksiyonu
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Şifre hashleme fonksiyonu
def get_password_hash(password):
    return pwd_context.hash(password)

# JWT oluşturma fonksiyonu
def create_access_token(data: dict):
    to_encode = data.copy() # Veriyi kopyala
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Token'ın son kullanma tarihini ayarla
    to_encode.update({"exp": expire}) # Son kullanma tarihini token verisine ekle
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # JWT'yi şifrele
    return encoded_jwt

# Eski LoginRequest modeli, Form() kullanımı için artık doğrudan endpoint'te kullanılmayacak.
# Bu modeli isterseniz silebilirsiniz, ancak manuel JSON POST testleri için saklamak isteyebilirsiniz.
# class LoginRequest(BaseModel):
#     username: str
#     password: str

# Kullanıcı kaydı isteği için Pydantic modeli
class RegisterRequest(BaseModel):
    username: str # Kullanıcı adı alanı
    password: str # Şifre alanı
    # is_admin: bool = False # Kullanıcının kendini admin yapmasını engellemek için bu satırı SİLDİK

# Token verisi için Pydantic modeli
class TokenData(BaseModel):
    username: Optional[str] = None # Token içindeki kullanıcı adı

# Giriş endpoint'i - Burası Form verisi kabul edecek şekilde GÜNCELLENDİ
@router.post("/login", summary="Authenticate user and get JWT token")
def login(
    # Bu endpoint'e gelecek olan kullanıcı adı ve şifre bilgilerini Form verisi olarak alıyoruz.
    # Swagger UI'daki "Authorize" butonu da bu formatı kullanır.
    username: str = Form(...), # Kullanıcı adını zorunlu bir form alanı olarak al
    password: str = Form(...), # Şifreyi zorunlu bir form alanı olarak al
    db: Session = Depends(get_db) # Veritabanı oturumu bağımlılığı
):
    # Kullanıcıyı veritabanında bul
    user = db.query(User).filter(User.username == username).first()
    # Kullanıcı yoksa veya şifre yanlışsa hata döndür
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    # Erişim token'ı oluştur
    access_token = create_access_token(data={"sub": user.username})
    return {
        "username": user.username,
        "token": access_token,
        "token_type": "bearer",
        "is_admin": user.is_admin
    }

# Kullanıcı kayıt endpoint'i - is_admin'in her zaman False olmasını GARANTİ EDİLDİ
@router.post("/register", summary="Register a new user")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Kullanıcı adının zaten kayıtlı olup olmadığını kontrol et
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Şifreyi hashle
    hashed_password = get_password_hash(request.password)

    # Yeni kullanıcı objesini oluştur
    # is_admin değeri doğrudan 'False' olarak atandı, client'tan gelen değer göz ardı edilir.
    new_user = User(
        username=request.username,
        password=hashed_password,
        is_admin=False # BURASI KESİNLİKLE FALSE OLACAK
    )
    # Kullanıcıyı veritabanına ekle
    db.add(new_user)
    db.commit() # Değişiklikleri kaydet
    db.refresh(new_user) # Objenin güncel halini al

    return {
        "message": "User registered successfully",
        "username": new_user.username,
        "is_admin": new_user.is_admin
    }

# Mevcut aktif kullanıcıyı döndüren bağımlılık (dependency)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    HTTP Bearer token'dan kullanıcıyı doğrular ve User objesini döndürür.
    Geçersiz token veya kullanıcı bulunamazsa HTTP 401 hatası fırlatır.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Token'ı çöz ve kullanıcı adını al
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # 'sub' alanı kullanıcı adını içerir
        if username is None:
            raise credentials_exception # Kullanıcı adı yoksa hata fırlat
        token_data = TokenData(username=username) # Token verisi Pydantic modeli
    except JWTError:
        raise credentials_exception # JWT çözme hatası varsa hata fırlat

    # Kullanıcıyı veritabanından bul
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception # Kullanıcı veritabanında yoksa hata fırlat
    return user # Doğrulanmış User objesini döndür

# Mevcut aktif admin kullanıcıyı döndüren bağımlılık
async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Mevcut kullanıcının admin olup olmadığını kontrol eder.
    Admin değilse HTTP 403 hatası fırlatır.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user # Admin User objesini döndür