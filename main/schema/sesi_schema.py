from sqlmodel import SQLModel, Field
from datetime import time

class Sesi(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    __tablename__: str = "data_sesi"

    id: int = Field(default=None, primary_key=True)
    acara: str = Field(index=True)
    sesi: str = Field(index=True)
    waktu: time = Field(default=None)
