from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class AbsenAsramaanBase(SQLModel):
    acara: str = Field(index=True)
    tanggal: datetime
    jam_hadir: str
    nama: str = Field(index=True)
    lokasi: str
    ranah: str
    detail_ranah: str
    sesi: str = Field(index=True)  # Added sesi field

    @field_validator('jam_hadir')
    def validate_jam_hadir(cls, v):
        try:
            # Parse time string and reformat to ensure HH:mm format
            parsed_time = datetime.strptime(v, '%H:%M')
            return parsed_time.strftime('%H:%M')
        except ValueError:
            raise ValueError('jam_hadir must be in HH:mm format')

class AbsenAsramaan(AbsenAsramaanBase, table=True):
    __table_args__ = {'extend_existing': True}
    __tablename__:str = 'rec_absen_asramaan'
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AbsenAsramaanCreate(AbsenAsramaanBase):
    pass

class AbsenAsramaanRead(AbsenAsramaanBase):
    id: int
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d')
        }
