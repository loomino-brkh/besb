from sqlmodel import SQLModel, Field
from datetime import time

class Sesi(SQLModel, table=True):
    __tablename__: str = "data_sesi"
    
    id: int = Field(default=None, primary_key=True)
    acara: str = Field(index=True)
    sesi: str
    waktu: time = Field(default=None)