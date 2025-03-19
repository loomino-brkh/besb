from sqlmodel import SQLModel, Field

class DataDaerah(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    __tablename__: str = "data_daerah"

    id: int = Field(default=None, primary_key=True)
    daerah: str = Field(index=True)
    ranah: str
    detail_ranah: str
