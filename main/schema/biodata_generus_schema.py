import json
from datetime import date
from typing import ClassVar, Dict, Optional, Union

from pydantic import field_validator
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class BiodataGenerusBase(SQLModel):
    nama_lengkap: str
    nama_panggilan: str
    kelahiran_tempat: str
    kelahiran_tanggal: date
    alamat_tinggal: str
    pendataan_tanggal: date
    sambung_desa: str
    sambung_kelompok: str
    hobi: Optional[Dict[str, str]] = Field(default=None, sa_type=JSON)
    sekolah_kelas: str
    nomor_hape: Optional[str] = None
    nama_ayah: str
    nama_ibu: str
    status_ayah: str
    status_ibu: str
    nomor_hape_ayah: Optional[str] = None
    nomor_hape_ibu: Optional[str] = None
    jenis_kelamin: str
    daerah: str


class BiodataGenerusCreate(BiodataGenerusBase):
    pass


class BiodataGenerusModel(BiodataGenerusBase, table=True):
    __table_args__ = {"extend_existing": True}
    __tablename__: ClassVar[str] = "data_biodata_generus"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: str = Field(default_factory=lambda: date.today().isoformat())


class BiodataGenerusResponse(BiodataGenerusBase):
    id: int
    created_at: str

    @field_validator("hobi", mode="before")
    def ensure_hobi_dict(
        cls, v: Optional[Union[Dict[str, str], str]]
    ) -> Optional[Dict[str, str]]:
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                raise ValueError("hobi must be a valid JSON dictionary")
        return v


class BiodataGenerusGetResponse(SQLModel):
    nama_lengkap: str
    nama_panggilan: str
    sambung_desa: str
    sambung_kelompok: str
    jenis_kelamin: str
