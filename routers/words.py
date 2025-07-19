from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.word import Word

router = APIRouter()

@router.get("/words/")
def get_words(db: Session = Depends(get_db)):
    return db.query(Word).all()

@router.get("/word/{word_id}")
def get_words(word_id: int, db: Session = Depends(get_db)):
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if db_word is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return db_word

@router.post("/words/")
def add_word(word: dict, db: Session = Depends(get_db)):
    db_word = Word(**word)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

@router.put("/words/{word_id}")
def update_word(word_id: int, word_data: dict, db: Session = Depends(get_db)):
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")

    for key, value in word_data.items():
        setattr(db_word, key, value)

    db.commit()
    return db_word

@router.delete("/words/{word_id}")
def delete_word(word_id: int, db: Session = Depends(get_db)):
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")

    db.delete(db_word)
    db.commit()
    return {"message": "Word deleted"}