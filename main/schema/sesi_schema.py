from sqlmodel import SQLModel, Field
from datetime import time

class Sesi(SQLModel, table=True):
    __tablename__ = "data_sesi" # type: ignore
    
    id: int = Field(default=None, primary_key=True)
    acara: str = Field(index=True)
    sesi: str
    waktu: time = Field(default=None)