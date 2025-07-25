from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter()

@router.post("/entries/", response_model=schemas.DictionaryEntry)
def create_entry(
    entry: schemas.DictionaryEntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_entry = models.DictionaryEntry(**entry.dict(), owner_id=current_user.id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/entries/", response_model=list[schemas.DictionaryEntry])
def read_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.DictionaryEntry).offset(skip).limit(limit).all()

@router.put("/entries/{entry_id}", response_model=schemas.DictionaryEntry)
def update_entry(
    entry_id: int,
    entry: schemas.DictionaryEntryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_entry = db.query(models.DictionaryEntry).filter(models.DictionaryEntry.id == entry_id).first()

    if not db_entry:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    if db_entry.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Yetkiniz yok")

    for var, value in vars(entry).items():
        setattr(db_entry, var, value) if value else None

    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/entries/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Sadece admin silme işlemi yapabilir")

    db_entry = db.query(models.DictionaryEntry).filter(models.DictionaryEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")

    db.delete(db_entry)
    db.commit()
    return {"mesaj": "Kayıt başarıyla silindi"}