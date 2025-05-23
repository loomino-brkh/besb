from typing import Dict, List

from core.db import get_async_db
from fastapi import APIRouter, Depends, HTTPException
from schema.data_kelas_sekolah_schema import DataKelasSekolah
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

router = APIRouter()


@router.get("/", response_model=List[Dict[str, str]])
async def get_kelas_sekolah_data(
    db: AsyncSession = Depends(get_async_db),
) -> List[Dict[str, str]]:
    """Get all school class data"""
    try:
        query = select(DataKelasSekolah)
        result = await db.execute(query)
        data = result.scalars().all()

        if not data:
            return []  # Empty list of the expected return type

        return [{"jenjang": item.jenjang, "kelas": item.kelas} for item in data]
    except Exception as e:
        import traceback

        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }
        print("Database Error Details:", error_details)
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {error_details['error_type']} - {error_details['error_message']}",
        )
