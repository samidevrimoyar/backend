from pydantic import BaseModel

class DictionaryEntryBase(BaseModel):
    word: str
    definition: str
    example: str | None = None

class DictionaryEntryCreate(DictionaryEntryBase):
    pass

class DictionaryEntryUpdate(DictionaryEntryBase):
    pass

class DictionaryEntry(DictionaryEntryBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True