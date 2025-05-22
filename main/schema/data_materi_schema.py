from typing import ClassVar

from sqlmodel import Field, SQLModel


class DataMateri(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__: ClassVar[str] = "data_materi"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    kategori: str = Field(index=True)
    detail_kategori: str = Field(default="")
    materi: str = Field(default="")
    detail_materi: str = Field(default="")
    indikator: str = Field(default="")
    indikator_mulai: str = Field(default="")
    indikator_akhir: str = Field(default="")
