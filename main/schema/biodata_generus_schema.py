from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class BiodataGenerusBase(SQLModel):
    nama_lengkap: str
    nama_panggilan: str
    kelahiran_tempat: str
    kelahiran_tanggal: date
    alamat_tinggal: str
    pendataan_tanggal: date
    sambung_desa: str
    sambung_kelompok: str
    hobi: str
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


class BiodataGenerusModel(BiodataGenerusBase, SQLModel, table=True):
    __tablename__: str = "biodata_generus"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: str = Field(default_factory=lambda: date.today().isoformat())


class BiodataGenerusResponse(BiodataGenerusBase):
    id: int
    created_at: str


class BiodataGenerusGetResponse(SQLModel):
    nama_lengkap: str
    nama_panggilan: str
    sambung_desa: str
    sambung_kelompok: str
    jenis_kelamin: str
