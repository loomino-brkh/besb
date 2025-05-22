from datetime import time
from typing import ClassVar

from sqlmodel import Field, SQLModel


class Sesi(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__: ClassVar[str] = "data_sesi"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    acara: str = Field(index=True)
    sesi: str = Field(index=True)
    waktu: time = Field(default=None)
