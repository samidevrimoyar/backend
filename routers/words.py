from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload # SQLAlchemy oturumu ve joinedload için
from typing import List, Optional # Tip hint'leri için
from database import get_db # Veritabanı oturumu almak için
from models.word import Word, WordCreate, WordUpdate, WordResponse # Word modellerini ve Pydantic şemalarını içe aktarın
from models.user import User # User modelini içe aktarın (ilişki için)
from routers.auth import get_current_user, get_current_admin_user # Kimlik doğrulama bağımlılıklarını içe aktarın

router = APIRouter()

# Yeni kelime oluşturma endpoint'i
@router.post("/", response_model=WordResponse, status_code=status.HTTP_201_CREATED, summary="Create a new word entry")
async def create_word(
    word: WordCreate, # Kelime oluşturma şeması (Pydantic modeli)
    db: Session = Depends(get_db), # Veritabanı oturumu bağımlılığı
    current_user: User = Depends(get_current_user) # Mevcut kullanıcı bağımlılığı (kimlik doğrulama)
):
    """
    Yeni bir kelime girişi oluşturur. Sadece oturum açmış kullanıcılar kelime ekleyebilir.
    """
    # Kelimenin zaten var olup olmadığını kontrol et
    existing_word = db.query(Word).filter(Word.word_text == word.word_text).first()
    if existing_word:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word with this text already exists."
        )

    # Yeni Word veritabanı objesini oluştur
    db_word = Word(
        word_text=word.word_text,
        definition=word.definition,
        created_by_user_id=current_user.id # Kelimeyi oluşturan kullanıcının ID'si
    )
    db.add(db_word) # Objeyi oturuma ekle
    db.commit() # Değişiklikleri veritabanına kaydet
    db.refresh(db_word) # Oluşturulan objeyi güncel verilerle yenile
    return db_word # Oluşturulan kelime objesini döndür (WordResponse şemasına göre dönüştürülür)

# Tüm kelimeleri listeleme endpoint'i
@router.get("/", response_model=List[WordResponse], summary="Retrieve all word entries")
async def get_words(
    db: Session = Depends(get_db), # Veritabanı oturumu bağımlılığı
    skip: int = Query(0, ge=0), # Listelemede atlanacak kayıt sayısı (varsayılan 0, negatif olamaz)
    limit: int = Query(100, ge=1, le=100) # Listelenecek maksimum kayıt sayısı (varsayılan 100, 1-100 arası)
):
    """
    Tüm sözlük kelimelerini listeler. Sayfalama (pagination) destekler.
    """
    # Veritabanından kelimeleri al (ilişkili kullanıcı verisini de yükleyerek)
    words = db.query(Word).options(joinedload(Word.creator)).offset(skip).limit(limit).all()
    return words # Kelime listesini döndür

# Belirli bir kelimeyi getirme endpoint'i
@router.get("/{word_id}", response_model=WordResponse, summary="Retrieve a single word entry by ID")
async def get_word(
    word_id: int, # URL'den gelen kelime ID'si
    db: Session = Depends(get_db) # Veritabanı oturumu bağımlılığı
):
    """
    Belirtilen ID'ye sahip sözlük kelimesini döndürür.
    """
    # Kelimeyi veritabanından ID'ye göre bul
    word = db.query(Word).options(joinedload(Word.creator)).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found."
        )
    return word # Bulunan kelimeyi döndür

# Kelime güncelleme endpoint'i
@router.put("/{word_id}", response_model=WordResponse, summary="Update an existing word entry")
async def update_word(
    word_id: int, # URL'den gelen kelime ID'si
    word_update: WordUpdate, # Kelime güncelleme şeması (Pydantic modeli)
    db: Session = Depends(get_db), # Veritabanı oturumu bağımlılığı
    current_user: User = Depends(get_current_user) # Mevcut kullanıcı bağımlılığı
):
    """
    Mevcut bir kelimeyi günceller. Sadece kelimeyi oluşturan kullanıcı veya bir admin güncelleyebilir.
    """
    # Kelimeyi veritabanından bul
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found."
        )

    # Yetkilendirme kontrolü: Kelimeyi oluşturan mı yoksa admin mi?
    if db_word.created_by_user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this word. You must be the creator or an admin."
        )

    # Güncellenecek alanları belirle ve uygula
    update_data = word_update.model_dump(exclude_unset=True) # Sadece gönderilen alanları al
    for key, value in update_data.items():
        setattr(db_word, key, value) # Model objesinin ilgili alanını güncelle

    db.add(db_word) # Değişiklikleri kaydetmek için tekrar ekle (bazı durumlarda gerekli)
    db.commit() # Değişiklikleri veritabanına kaydet
    db.refresh(db_word) # Güncellenen objeyi yenile
    return db_word # Güncellenen kelimeyi döndür

# Kelime silme endpoint'i (sadece adminler)
@router.delete("/{word_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a word entry (Admin only)")
async def delete_word(
    word_id: int, # URL'den gelen kelime ID'si
    db: Session = Depends(get_db), # Veritabanı oturumu bağımlılığı
    current_admin: User = Depends(get_current_admin_user) # Admin kullanıcı bağımlılığı (yetkilendirme)
):
    """
    Belirtilen ID'ye sahip kelimeyi siler. Sadece admin yetkisine sahip kullanıcılar silebilir.
    """
    # Kelimeyi veritabanından bul
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found."
        )

    db.delete(db_word) # Objeyi veritabanından sil
    db.commit() # Değişiklikleri kaydet
    return # 204 No Content döndür (başarılı silme)

# Kelimeyi admin onayı verme endpoint'i (sadece adminler)
@router.patch("/{word_id}/approve", response_model=WordResponse, summary="Approve a word entry (Admin only)")
async def approve_word(
    word_id: int, # URL'den gelen kelime ID'si
    db: Session = Depends(get_db), # Veritabanı oturumu bağımlılığı
    current_admin: User = Depends(get_current_admin_user) # Admin kullanıcı bağımlılığı
):
    """
    Belirtilen ID'ye sahip kelimeyi admin olarak onaylar. Sadece admin yetkisine sahip kullanıcılar yapabilir.
    """
    # Kelimeyi veritabanından bul
    db_word = db.query(Word).filter(Word.id == word_id).first()
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found."
        )

    # Kelimeyi onaylı olarak işaretle
    db_word.is_admin_approved = True

    db.add(db_word) # Değişiklikleri kaydetmek için tekrar ekle
    db.commit() # Değişiklikleri veritabanına kaydet
    db.refresh(db_word) # Güncellenen objeyi yenile
    return db_word # Onaylanan kelimeyi döndür