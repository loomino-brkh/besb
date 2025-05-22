from typing import ClassVar

from sqlmodel import Field, SQLModel


class DataDaerah(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__: ClassVar[str] = "data_daerah"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    daerah: str = Field(index=True)
    ranah: str
    detail_ranah: str
