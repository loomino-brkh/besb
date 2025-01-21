from sqlmodel import SQLModel, Field

class DataSesi(SQLModel, table=True):
    __tablename__ = "sesi"
    
    id: int = Field(default=None, primary_key=True)
    acara: str = Field(index=True)
    sesi: str