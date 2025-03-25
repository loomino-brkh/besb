from sqlmodel import SQLModel, Field


class DataHobi(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    __tablename__: str = "data_hobi"

    id: int = Field(default=None, primary_key=True)
    kategori: str = Field(index=True)
    hobi: str


class DataHobiCreate(DataHobi):
    pass
