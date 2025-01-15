from fastapi import APIRouter, HTTPException, Depends, Form
from sqlmodel import Session, select
from fastapi.concurrency import run_in_threadpool
from typing import List
from datetime import datetime, date, timedelta
from schema.absen_schema import AbsenPengajian, AbsenPengajianCreate, AbsenPengajianRead
from core.db import get_db
from core.auth import verify_read_permission, verify_write_permission

router = APIRouter()

@router.post("/", response_model=AbsenPengajianRead, dependencies=[Depends(verify_write_permission)])
async def create_absen(
    acara: str = Form(),
    tanggal: str = Form(),
    jam_hadir: str = Form(),
    nama: str = Form(),
    lokasi: str = Form(),
    ranah: str = Form(),
    detail_ranah: str = Form()
):
    try:
        # Convert string date to datetime
        tanggal_dt = datetime.strptime(tanggal, '%Y-%m-%d')
        
        # Create AbsenPengajian instance
        db_absen = AbsenPengajian(
            acara=acara,
            tanggal=tanggal_dt,
            jam_hadir=jam_hadir,
            nama=nama,
            lokasi=lokasi,
            ranah=ranah,
            detail_ranah=detail_ranah
        )
        
        # Use the database session in a context manager
        with get_db() as db:
            db.add(db_absen)
            db.commit()
            db.refresh(db_absen)
            # Create a copy of the data before session closes
            result = AbsenPengajianRead.from_orm(db_absen)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date or time format. Date should be YYYY-MM-DD and time should be HH:MM. Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/", response_model=List[AbsenPengajianRead], dependencies=[Depends(verify_read_permission)])
async def list_absen(
    tanggal: str = None,
    acara: str = None
):
    try:
        with get_db() as db:
            query = select(AbsenPengajian)
            
            # Apply filters if parameters are provided
            if tanggal:
                try:
                    # Convert string date to datetime for comparison
                    filter_date = datetime.strptime(tanggal, '%Y-%m-%d')
                    # Compare only the date part
                    query = query.filter(AbsenPengajian.tanggal >= filter_date,
                                      AbsenPengajian.tanggal < filter_date + timedelta(days=1))
                except ValueError:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid date format. Date should be YYYY-MM-DD"
                    )
            
            if acara:
                query = query.filter(AbsenPengajian.acara == acara)
            
            absen_list = db.exec(query).all()
            # Convert to response model to ensure we have all data before session closes
            result = [AbsenPengajianRead.from_orm(absen) for absen in absen_list]
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/{absen_id}", response_model=AbsenPengajianRead, dependencies=[Depends(verify_auth)])
async def get_absen(absen_id: int):
    try:
        with get_db() as db:
            absen = db.get(AbsenPengajian, absen_id)
            if absen is None:
                raise HTTPException(status_code=404, detail="Absen record not found")
            # Convert to response model before session closes
            result = AbsenPengajianRead.from_orm(absen)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )