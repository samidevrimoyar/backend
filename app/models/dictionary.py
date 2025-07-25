from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class DictionaryEntry(Base):
    __tablename__ = "dictionary_entries"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    definition = Column(String)
    example = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Kullanıcıyla ilişki
    owner = relationship("User", back_populates="entries")