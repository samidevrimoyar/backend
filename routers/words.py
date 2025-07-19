from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.word import Word

router = APIRouter()

@router.get("/words/")
def get_words(
    db: Session = Depends(get_db),
    id: int = Query(None, description="Filtrelemek için kelime ID'si"),
    search: str = Query(None, description="Genel arama (kelime veya anlamda)"),
    limit: int = Query(100, description="Sayfa başı sonuç sayısı"),
    offset: int = Query(0, description="Sayfa ofset değeri")
):
    query = db.query(Word)

    # ID'ye göre filtreleme
    if id:
        query = query.filter(Word.id == id)

    # Genel arama (hem term hem definition üzerinde)
    if search:
        query = query.filter(Word.term.ilike(f"%{search}%"))

    # Sayfalama
    words = query.offset(offset).limit(limit).all()

    return words

@router.get("/words/{word_id}")
def get_word_by_id(word_id: int, db: Session = Depends(get_db)):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word

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