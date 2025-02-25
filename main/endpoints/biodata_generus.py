from fastapi import APIRouter, Depends, Form, HTTPException
from sqlmodel import Session, select  # updated import to include "select"
from typing import Optional
from datetime import date

from core.db import get_db
from core.auth import verify_write_permission
from schema.biodata_generus_schema import BiodataGenerusModel, BiodataGenerusResponse

router = APIRouter()

@router.get("/", response_model=list[BiodataGenerusResponse])
async def get_biodata():
    """
    Get all biodata entries for generus
    """
    try:
        with get_db() as db:
            # updated deprecated query syntax
            biodata = db.exec(select(BiodataGenerusModel)).all()
            result = [BiodataGenerusResponse(
                nama_lengkap=data.nama_lengkap,
                nama_panggilan=data.nama_panggilan,
                sambung_desa=data.sambung_desa,
                sambung_kelompok=data.sambung_kelompok
            ) for data in biodata]
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving biodata: {str(e)}")

@router.post("/", response_model=BiodataGenerusResponse, dependencies=[Depends(verify_write_permission)])
async def create_biodata(
    nama_lengkap: str = Form(...),
    nama_panggilan: str = Form(...),
    kelahiran_tempat: str = Form(...),
    kelahiran_tanggal: date = Form(...),
    alamat_tinggal: str = Form(...),
    pendataan_tanggal: date = Form(...),
    sambung_desa: str = Form(...),
    sambung_kelompok: str = Form(...),
    hobi: str = Form(...),
    sekolah_kelas: str = Form(...),
    nomor_hape: Optional[str] = Form(None),
    nama_ayah: str = Form(...),
    nama_ibu: str = Form(...),
    status_ayah: str = Form(...),
    status_ibu: str = Form(...)
):
    """
    Create a new biodata entry for generus
    """
    try:
        with get_db() as db:
            # Create biodata model
            biodata = BiodataGenerusModel(
                nama_lengkap=nama_lengkap,
                nama_panggilan=nama_panggilan,
                kelahiran_tempat=kelahiran_tempat,
                kelahiran_tanggal=kelahiran_tanggal,
                alamat_tinggal=alamat_tinggal,
                pendataan_tanggal=pendataan_tanggal,
                sambung_desa=sambung_desa,
                sambung_kelompok=sambung_kelompok,
                hobi=hobi,
                sekolah_kelas=sekolah_kelas,
                nomor_hape=nomor_hape,
                nama_ayah=nama_ayah,
                nama_ibu=nama_ibu,
                status_ayah=status_ayah,
                status_ibu=status_ibu
            )
            
            # Save to database
            db.add(biodata)
            db.commit()
            db.refresh(biodata)
            result = BiodataGenerusResponse(
                nama_lengkap=biodata.nama_lengkap,
                nama_panggilan=biodata.nama_panggilan,
                sambung_desa=biodata.sambung_desa,
                sambung_kelompok=biodata.sambung_kelompok
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating biodata: {str(e)}")
