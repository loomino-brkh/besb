from sqlmodel import SQLModel, Field

class DataMateri(SQLModel, table=True):
    __tablename__ = "data_materi"
    
    id: int = Field(default=None, primary_key=True)
    kategori: str = Field(index=True)
    detail_kategori: str
    materi: str
    detail_materi: str
    indikator: str
    indikator_mulai: str
    indikator_akhir: str
