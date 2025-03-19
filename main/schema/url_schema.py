from sqlmodel import SQLModel, Field
from typing import Optional
import string
import random

def generate_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class URLBase(SQLModel):
    url: str = Field(...)

class URL(URLBase, table=True):
    __table_args__ = {'extend_existing': True}
    __tablename__: str = "rec_shorten_urls"
    id: Optional[int] = Field(default=None, primary_key=True)
    url_code: str = Field(default_factory=lambda: generate_code(), unique=True)

class URLResponse(URLBase):
    url_code: str

class URLCreate(URLBase):
    pass
