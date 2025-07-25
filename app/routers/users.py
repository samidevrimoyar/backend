from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # E-posta kontrolü
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-posta zaten kayıtlı")

    # Şifreyi hashleme
    hashed_password = utils.get_password_hash(user.password)

    # Yeni kullanıcı oluştur
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_admin=False  # Varsayılan olarak admin değil
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/me", response_model=schemas.User)
def read_user_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@router.get("/users/", response_model=list[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    # Sadece admin tüm kullanıcıları görebilir
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users