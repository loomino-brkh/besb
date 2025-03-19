from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import Optional
from fastapi_cache.decorator import cache

from core.db import get_async_db
from schema.data_materi_schema import DataMateri

router = APIRouter()

async def handle_db_error(e: Exception):
    """Handle database errors and return appropriate HTTP exception"""
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

def format_materi_response(items):
    """Format database results into response structure"""
    return [{
        "materi": item[0],
        "detail_materi": item[1],
        "detail_kategori": item[2],
        "indikator": item[3],
        "indikator_mulai": item[4],
        "indikator_akhir": item[5]
    } for item in items]

def build_query(kategori: str, detail_kategori: Optional[str] = None):
    """Build the database query based on provided parameters"""
    query = select([
        DataMateri.materi,
        DataMateri.detail_materi,
        DataMateri.detail_kategori,
        DataMateri.indikator,
        DataMateri.indikator_mulai,
        DataMateri.indikator_akhir
    ])

    conditions = [DataMateri.kategori == kategori]
    if detail_kategori:
        conditions.append(DataMateri.detail_kategori == detail_kategori)

    return query.where(*conditions)

@router.get("/{kategori}")
@router.get("/{kategori}/{detail_kategori}")
@cache(expire=300)  # Cache for 5 minutes
async def get_data_materi(
    kategori: str,
    detail_kategori: Optional[str] = None,
    db=Depends(get_async_db)
):
    try:
        query = build_query(kategori, detail_kategori)
        result = await db.execute(query)
        data = result.all()

        if not data:
            error_msg = f"No data found for kategori: {kategori}"
            if detail_kategori:
                error_msg += f" and detail_kategori: {detail_kategori}"
            raise HTTPException(status_code=404, detail=error_msg)

        return format_materi_response(data)

    except HTTPException:
        raise
    except Exception as e:
        await handle_db_error(e)
