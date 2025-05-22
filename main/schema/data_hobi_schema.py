from typing import ClassVar

from sqlmodel import Field, SQLModel


class DataHobi(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__: ClassVar[str] = "data_hobi"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    kategori: str = Field(index=True)
    hobi: str


class DataHobiCreate(DataHobi):
    pass
