from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models.user import User # User modelini içe aktarın
from passlib.context import CryptContext
from jose import JWTError, jwt # python-jose kütüphanesinden içe aktarın
from datetime import datetime, timedelta
import os # Ortam değişkenlerini okumak için

router = APIRouter()

# Şifre hashleme için CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ortam değişkeninden gizli anahtarı al
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise Exception("SECRET_KEY environment variable not set.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Şifre doğrulama fonksiyonu
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Şifre hashleme fonksiyonu
def get_password_hash(password):
    return pwd_context.hash(password)

# JWT oluşturma fonksiyonu
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Giriş isteği için Pydantic modeli
class LoginRequest(BaseModel):
    username: str
    password: str

# Kullanıcı kaydı isteği için Pydantic modeli
class RegisterRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False # Varsayılan olarak admin değil

# Giriş endpoint'i
@router.post("/login", summary="Authenticate user and get JWT token")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "username": user.username,
        "token": access_token,
        "token_type": "bearer",
        "is_admin": user.is_admin
    }

# Kullanıcı kayıt endpoint'i
@router.post("/register", summary="Register a new user")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(request.password)

    new_user = User(
        username=request.username,
        password=hashed_password,
        is_admin=request.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "username": new_user.username,
        "is_admin": new_user.is_admin
    }