import json
from datetime import date
from typing import Optional

from core.auth import verify_read_permission, verify_write_permission
from core.db import get_db
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi_cache.decorator import cache
from schema.biodata_generus_schema import (
    BiodataGenerusGetResponse,
    BiodataGenerusModel,
    BiodataGenerusResponse,
)
from sqlmodel import select

router = APIRouter()


@router.get(
    "/",
    response_model=list[BiodataGenerusGetResponse],
    dependencies=[Depends(verify_read_permission)],
)
@cache(expire=300)  # Cache response for 5 minutes
async def get_biodata():
    """
    Get all biodata entries for generus
    """
    try:
        with get_db() as db:
            # updated deprecated query syntax
            biodata = db.exec(select(BiodataGenerusModel)).all()
            result = [
                BiodataGenerusGetResponse(
                    nama_lengkap=data.nama_lengkap,
                    nama_panggilan=data.nama_panggilan,
                    sambung_desa=data.sambung_desa,
                    sambung_kelompok=data.sambung_kelompok,
                    jenis_kelamin=data.jenis_kelamin,
                )
                for data in biodata
            ]
            return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving biodata: {str(e)}"
        )


@router.post(
    "/",
    response_model=BiodataGenerusResponse,
    dependencies=[Depends(verify_write_permission)],
)
async def create_biodata(
    request: Request,
    nama_lengkap: Optional[str] = Form(None),
    nama_panggilan: Optional[str] = Form(None),
    kelahiran_tempat: Optional[str] = Form(None),
    kelahiran_tanggal: Optional[date] = Form(None),
    alamat_tinggal: Optional[str] = Form(None),
    pendataan_tanggal: Optional[date] = Form(None),
    sambung_desa: Optional[str] = Form(None),
    sambung_kelompok: Optional[str] = Form(None),
    hobi: Optional[str] = Form(None),  # Keep as string in Form, will parse to dict
    sekolah_kelas: Optional[str] = Form(None),
    nomor_hape: Optional[str] = Form(None),
    nama_ayah: Optional[str] = Form(None),
    nama_ibu: Optional[str] = Form(None),
    status_ayah: Optional[str] = Form(None),
    status_ibu: Optional[str] = Form(None),
    nomor_hape_ayah: Optional[str] = Form(None),
    nomor_hape_ibu: Optional[str] = Form(None),
    jenis_kelamin: Optional[str] = Form(None),
    daerah: Optional[str] = Form(None),
):
    """
    Create a new biodata entry for generus
    Supports both form data and JSON input
    """
    try:
        content_type = request.headers.get("content-type", "")

        # Handle JSON input
        if "application/json" in content_type:
            body = await request.body()
            data = json.loads(body.decode())

            # Extract values from JSON
            nama_lengkap = data.get("nama_lengkap")
            nama_panggilan = data.get("nama_panggilan")
            kelahiran_tempat = data.get("kelahiran_tempat")
            kelahiran_tanggal = data.get("kelahiran_tanggal")
            alamat_tinggal = data.get("alamat_tinggal")
            pendataan_tanggal = data.get("pendataan_tanggal")
            sambung_desa = data.get("sambung_desa")
            sambung_kelompok = data.get("sambung_kelompok")
            hobi = data.get("hobi")
            sekolah_kelas = data.get("sekolah_kelas")
            nomor_hape = data.get("nomor_hape")
            nama_ayah = data.get("nama_ayah")
            nama_ibu = data.get("nama_ibu")
            status_ayah = data.get("status_ayah")
            status_ibu = data.get("status_ibu")
            nomor_hape_ayah = data.get("nomor_hape_ayah")
            nomor_hape_ibu = data.get("nomor_hape_ibu")
            jenis_kelamin = data.get("jenis_kelamin")
            daerah = data.get("daerah")

            # Convert date strings to date objects if needed
            if isinstance(kelahiran_tanggal, str):
                kelahiran_tanggal = date.fromisoformat(kelahiran_tanggal)
            if isinstance(pendataan_tanggal, str):
                pendataan_tanggal = date.fromisoformat(pendataan_tanggal)

        # Validate required fields
        required_fields = {
            "nama_lengkap": nama_lengkap,
            "nama_panggilan": nama_panggilan,
            "kelahiran_tempat": kelahiran_tempat,
            "kelahiran_tanggal": kelahiran_tanggal,
            "alamat_tinggal": alamat_tinggal,
            "pendataan_tanggal": pendataan_tanggal,
            "sambung_desa": sambung_desa,
            "sambung_kelompok": sambung_kelompok,
            "hobi": hobi,
            "sekolah_kelas": sekolah_kelas,
            "nama_ayah": nama_ayah,
            "nama_ibu": nama_ibu,
            "status_ayah": status_ayah,
            "status_ibu": status_ibu,
            "jenis_kelamin": jenis_kelamin,
            "daerah": daerah,
        }

        missing_fields = [
            field for field, value in required_fields.items() if value is None
        ]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}",
            )

        # After validation, we know these fields are not None
        assert nama_lengkap is not None
        assert nama_panggilan is not None
        assert kelahiran_tempat is not None
        assert kelahiran_tanggal is not None
        assert alamat_tinggal is not None
        assert pendataan_tanggal is not None
        assert sambung_desa is not None
        assert sambung_kelompok is not None
        assert sekolah_kelas is not None
        assert nama_ayah is not None
        assert nama_ibu is not None
        assert status_ayah is not None
        assert status_ibu is not None
        assert jenis_kelamin is not None
        assert daerah is not None

        # Validate hobi doesn't contain square brackets
        if hobi and ("[" in hobi or "]" in hobi):
            raise HTTPException(
                status_code=400,
                detail="Invalid hobi format: square brackets are not allowed",
            )

        # Parse hobi from JSON string to dictionary if it's a string
        if hobi is None:
            hobi_dict = None
        else:  # hobi is str
            hobi_dict = json.loads(hobi) if hobi else None

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
                hobi=hobi_dict,
                sekolah_kelas=sekolah_kelas,
                nomor_hape=nomor_hape,
                nama_ayah=nama_ayah,
                nama_ibu=nama_ibu,
                status_ayah=status_ayah,
                status_ibu=status_ibu,
                nomor_hape_ayah=nomor_hape_ayah,
                nomor_hape_ibu=nomor_hape_ibu,
                jenis_kelamin=jenis_kelamin,
                daerah=daerah,
            )

            db.add(biodata)
            db.commit()
            db.refresh(biodata)
            result = BiodataGenerusResponse.model_validate(biodata)

        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating biodata: {str(e)}")
