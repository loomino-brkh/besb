from typing import ClassVar, Optional

from sqlmodel import Field, SQLModel


class DataKelasSekolah(SQLModel, table=True):
    __table_arg__ = {"extend_existing": True}
    __tablename__: ClassVar[str] = "data_kelas_sekolah"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    jenjang: str
    kelas: str


class DataKelasSekolahCreate(DataKelasSekolah):
    pass
