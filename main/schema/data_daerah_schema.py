from sqlmodel import SQLModel, Field

class DataDaerah(SQLModel, table=True):
    __tablename__ = "data_daerah" # type: ignore
    
    id: int = Field(default=None, primary_key=True)
    daerah: str = Field(index=True)
    ranah: str
    detail_ranah: str