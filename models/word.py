from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship # İlişkileri tanımlamak için
from models.base import BaseModel # models/base.py dosyasındaki BaseModel'i içe aktarın
from pydantic import BaseModel as PydanticBaseModel # Pydantic BaseModel'i SQLAlchemy modelinden ayırmak için yeniden adlandırın
from typing import Optional # Alanların isteğe bağlı olabileceğini belirtmek için
from datetime import datetime

# Veritabanı Modeli (SQLAlchemy)
class Word(BaseModel):
    """
    Sözlükteki her bir kelime kaydını temsil eden veritabanı modeli.
    BaseModel'den miras alarak created_at ve updated_at alanlarını otomatik alır.
    """
    __tablename__ = "words" # Veritabanındaki tablo adı

    id = Column(Integer, primary_key=True, index=True) # Kelime kaydının benzersiz ID'si, birincil anahtar
    word_text = Column(String, unique=True, index=True, nullable=False) # Kelimenin kendisi, benzersiz olmalı, boş bırakılamaz
    definition = Column(String, nullable=False) # Kelimenin tanımı, boş bırakılamaz

    # ForeignKey ile User modeli ile ilişki kurulur.
    # Bu kelime kaydını hangi kullanıcının eklediğini belirtir.
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # İlişki tanımlaması: Word modelinden User modeline erişim sağlar.
    # backref="words" User modelinden bu kullanıcının tüm kelimelerine erişim sağlar.
    creator = relationship("User", backref="words")

    # Admin tarafından onaylanıp onaylanmadığı. Varsayılan olarak False.
    is_admin_approved = Column(Boolean, default=False)

    def __repr__(self):
        """Modelin okunabilir bir temsilini sağlar, hata ayıklama için faydalıdır."""
        return f"<Word(id={self.id}, word_text='{self.word_text}')>"

# Pydantic Şemaları (Veri Doğrulama ve Seri hale Getirme)

# Kelime oluşturma isteği için şema (Client'tan gelen veri)
class WordCreate(PydanticBaseModel):
    """
    Yeni bir kelime kaydı oluşturmak için kullanılan veri şeması.
    Client'ın göndereceği verileri tanımlar.
    """
    word_text: str # Zorunlu: Kelimenin metni
    definition: str # Zorunlu: Kelimenin tanımı

    class Config:
        from_attributes = True # SQLAlchemy modellerinden Pydantic'e dönüşümü sağlar (FastAPI'da önerilen)

# Kelime güncelleme isteği için şema (Client'tan gelen veri)
class WordUpdate(PydanticBaseModel):
    """
    Mevcut bir kelime kaydını güncellemek için kullanılan veri şeması.
    Alanlar Optional olduğu için sadece gönderilen alanlar güncellenir.
    """
    word_text: Optional[str] = None # İsteğe bağlı: Kelimenin metni
    definition: Optional[str] = None # İsteğe bağlı: Kelimenin tanımı

    class Config:
        from_attributes = True

# Kelime yanıtı için şema (API'dan Client'a dönen veri)
class WordResponse(PydanticBaseModel):
    """
    API'dan kelime kaydı döndürülürken kullanılan veri şeması.
    Veritabanındaki tüm ilgili alanları içerir.
    """
    id: int # Kelime ID'si
    word_text: str # Kelimenin metni
    definition: str # Kelimenin tanımı
    created_by_user_id: int # Kelimeyi ekleyen kullanıcının ID'si
    is_admin_approved: bool # Admin tarafından onaylanma durumu
    created_at: datetime # Oluşturulma zamanı (BaseModel'den gelir)
    updated_at: datetime # Güncellenme zamanı (BaseModel'den gelir)

    class Config:
        from_attributes = True