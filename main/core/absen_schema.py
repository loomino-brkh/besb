from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import validator

class AbsenPengajianBase(SQLModel):
    acara: str = Field(index=True)
    tanggal: datetime
    jam_hadir: str
    nama: str = Field(index=True)
    lokasi: str
    ranah: str
    detail_ranah: str

    @validator('jam_hadir')
    def validate_jam_hadir(cls, v):
        try:
            # Parse time string and reformat to ensure HH:mm format
            parsed_time = datetime.strptime(v, '%H:%M')
            return parsed_time.strftime('%H:%M')
        except ValueError:
            raise ValueError('jam_hadir must be in HH:mm format')

class AbsenPengajian(AbsenPengajianBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AbsenPengajianCreate(AbsenPengajianBase):
    pass

class AbsenPengajianRead(AbsenPengajianBase):
    id: int
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%Y-%m-%d')
        }