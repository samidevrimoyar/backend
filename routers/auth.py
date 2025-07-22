from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise Exception("SECRET_KEY environment variable not set.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class LoginRequest(BaseModel):
    username: str
    password: str

# Yeni kullanıcı kayıt isteği için Pydantic modeli
class RegisterRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False # Varsayılan olarak admin değil

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {
        "username": user.username,
        "token": access_token,
        "is_admin": user.is_admin
    }

# Yeni kullanıcı kayıt endpoint'i
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Kullanıcının zaten var olup olmadığını kontrol et
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Şifreyi hash'le
    hashed_password = get_password_hash(request.password)

    # Yeni kullanıcıyı oluştur
    new_user = User(
        username=request.username,
        password=hashed_password,
        is_admin=request.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Veritabanından güncel bilgileri çek

    return {
        "message": "User registered successfully",
        "username": new_user.username,
        "is_admin": new_user.is_admin
    }
