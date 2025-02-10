from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List

from core.db import get_async_db
from schema.data_materi_schema import DataMateri

router = APIRouter()

@router.get("/{kategori}")
async def get_data_by_kategori(
    kategori: str,
    db=Depends(get_async_db)
):
    query = select(
        DataMateri.materi,
        DataMateri.detail_materi,
        DataMateri.detail_kategori,
        DataMateri.indikator,
        DataMateri.indikator_mulai,
        DataMateri.indikator_akhir
    ).where(DataMateri.kategori == kategori)
    
    try:
        result = await db.execute(query)
        data = result.all()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for kategori: {kategori}")
        
        return [{
            "materi": item[0],
            "detail_materi": item[1],
            "detail_kategori": item[2],
            "indikator": item[3],
            "indikator_mulai": item[4],
            "indikator_akhir": item[5]
        } for item in data]
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        print("Database Error Details:", error_details)  # For logging
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {error_details['error_type']} - {error_details['error_message']}"
        )
