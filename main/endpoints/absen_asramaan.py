from datetime import datetime, timedelta
from typing import List, Optional

from core.auth import verify_read_permission, verify_write_permission
from core.db import get_db
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi_cache.decorator import cache
from schema.absen_asramaan_schema import AbsenAsramaan, AbsenAsramaanRead
from sqlmodel import Session, and_, select

router = APIRouter()


async def check_duplicate_asramaan(
    db: Session,
    acara: str,
    tanggal: datetime,
    nama: str,
    lokasi: str,
    ranah: str,
    detail_ranah: str,
    sesi: str,
) -> bool:
    # Get the time window (2 hours before and after current time)
    time_window_start = tanggal - timedelta(hours=2)
    time_window_end = tanggal + timedelta(hours=2)

    # Query for duplicates within time window
    query = select(AbsenAsramaan).where(
        AbsenAsramaan.acara == acara,
        AbsenAsramaan.nama == nama,
        AbsenAsramaan.lokasi == lokasi,
        AbsenAsramaan.ranah == ranah,
        AbsenAsramaan.detail_ranah == detail_ranah,
        AbsenAsramaan.sesi == sesi,
        AbsenAsramaan.tanggal >= time_window_start,
        AbsenAsramaan.tanggal <= time_window_end,
    )

    result = db.exec(query).first()
    return result is not None


@router.post(
    "/",
    response_model=AbsenAsramaanRead,
    dependencies=[Depends(verify_write_permission)],
)
async def create_absen(
    acara: str = Form(),
    tanggal: str = Form(),
    jam_hadir: str = Form(),
    nama: str = Form(),
    lokasi: str = Form(),
    ranah: str = Form(),
    detail_ranah: str = Form(),
    sesi: str = Form(),
):
    try:
        # Convert string date to datetime and add time component from jam_hadir
        tanggal_dt = datetime.strptime(tanggal, "%Y-%m-%d")
        full_dt = datetime.combine(
            tanggal_dt.date(), datetime.strptime(jam_hadir, "%H:%M").time()
        )

        # Use the database session in a context manager
        with get_db() as db:
            # Check for duplicates
            is_duplicate = await check_duplicate_asramaan(
                db=db,
                acara=acara,
                tanggal=full_dt,
                nama=nama,
                lokasi=lokasi,
                ranah=ranah,
                detail_ranah=detail_ranah,
                sesi=sesi,
            )

            if is_duplicate:
                raise HTTPException(
                    status_code=409,
                    detail="Duplicate entry detected: Similar attendance record exists within 2 hours",
                )

            # Create AbsenAsramaan instance
            db_absen = AbsenAsramaan(
                acara=acara,
                tanggal=full_dt,
                jam_hadir=jam_hadir,
                nama=nama,
                lokasi=lokasi,
                ranah=ranah,
                detail_ranah=detail_ranah,
                sesi=sesi,
            )

            db.add(db_absen)
            db.commit()
            db.refresh(db_absen)
            # Create a copy of the data before session closes
            result = AbsenAsramaanRead.model_validate(db_absen)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date or time format. Date should be YYYY-MM-DD and time should be HH:MM. Error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get(
    "/",
    response_model=List[AbsenAsramaanRead],
    dependencies=[Depends(verify_read_permission)],
)
@cache(expire=300)  # Cache for 5 minutes
async def list_absen(
    tanggal: Optional[str] = None,
    acara: Optional[str] = None,
    sesi: Optional[str] = None,
    lokasi: Optional[str] = None,
):
    try:
        with get_db() as db:
            query = select(AbsenAsramaan)

            # Apply filters if parameters are provided
            if tanggal:
                try:
                    # Convert string date to datetime for comparison
                    filter_date = datetime.strptime(tanggal, "%Y-%m-%d")
                    # Compare only the date part
                    query = query.filter(
                        and_(
                            AbsenAsramaan.tanggal >= filter_date,
                            AbsenAsramaan.tanggal < filter_date + timedelta(days=1),
                        )
                    )
                except ValueError:
                    raise HTTPException(
                        status_code=422,
                        detail="Invalid date format. Date should be YYYY-MM-DD",
                    )

            if acara:
                query = query.filter(and_(AbsenAsramaan.acara == acara))

            if sesi:
                query = query.filter(and_(AbsenAsramaan.sesi == sesi))

            if lokasi:
                query = query.filter(and_(AbsenAsramaan.lokasi == lokasi))

            absen_list = db.exec(query).all()
            # Convert to response model to ensure we have all data before session closes
            result = [AbsenAsramaanRead.model_validate(absen) for absen in absen_list]
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get(
    "/{absen_id}",
    response_model=AbsenAsramaanRead,
    dependencies=[Depends(verify_read_permission)],
)
@cache(expire=300)  # Cache for 5 minutes
async def get_absen(absen_id: int):
    try:
        with get_db() as db:
            absen = db.get(AbsenAsramaan, absen_id)
            if absen is None:
                raise HTTPException(status_code=404, detail="Absen record not found")
            # Convert to response model before session closes
            result = AbsenAsramaanRead.model_validate(absen)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
