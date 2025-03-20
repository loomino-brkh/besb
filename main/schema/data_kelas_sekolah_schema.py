from sqlmodel import SQLModel, Field
from typing import Optional

class DataKelasSekolah(SQLModel, table=True):
    __table_arg__: dict = {"extend_existing": True}
    __tablename__: str = "data_kelas_sekolah"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    jenjang: str
    kelas: str

class DataKelasSekolahCreate(DataKelasSekolah):
    pass