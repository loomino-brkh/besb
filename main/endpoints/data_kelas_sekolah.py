from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from fastapi_cache.decorator import cache

from core.db import get_async_db
from schema.data_kelas_sekolah_schema import DataKelasSekolah

router = APIRouter()

@router.get("/")
@cache(expire=300)  # Cache for 5 minutes
async def get_kelas_sekolah_data(
    db=Depends(get_async_db)
):
    """Get all school class data"""
    try:
        query = select(DataKelasSekolah)
        result = await db.execute(query)
        data = result.scalars().all()

        if not data:
            return []

        return [{"jenjang": item.jenjang, "kelas": item.kelas} for item in data]
    except Exception as e:
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        print("Database Error Details:", error_details)
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {error_details['error_type']} - {error_details['error_message']}"
        )
