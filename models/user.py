from sqlalchemy import Column, Integer, String, Boolean
from models.base import BaseModel # BaseModel'i models/base.py'den içe aktarın

class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False) # Hashlenmiş şifre
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', is_admin={self.is_admin})>"