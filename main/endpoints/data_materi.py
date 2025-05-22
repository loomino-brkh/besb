from typing import Any, Dict, List, Optional, Sequence

from core.db import get_async_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from schema.data_materi_schema import DataMateri
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlmodel import select

router = APIRouter()


async def handle_db_error(e: Exception):
    """Handle database errors and return appropriate HTTP exception"""
    import traceback

    error_details = {
        "error_type": type(e).__name__,
        "error_message": str(e),
        "traceback": traceback.format_exc(),
    }

    print("Database Error Details:", error_details)  # For logging
    raise HTTPException(
        status_code=500,
        detail=f"Database error: {error_details['error_type']} - {error_details['error_message']}",
    )


def format_materi_response(items: Sequence[DataMateri]) -> List[Dict[str, Any]]:
    """Format database results into response structure"""
    return [
        {
            "materi": item.materi,
            "detail_materi": item.detail_materi,
            "detail_kategori": item.detail_kategori,
            "indikator": item.indikator,
            "indikator_mulai": item.indikator_mulai,
            "indikator_akhir": item.indikator_akhir,
        }
        for item in items
    ]


def build_query(
    kategori: str, detail_kategori: Optional[str] = None
) -> Select[tuple[DataMateri]]:
    """Build the database query based on provided parameters"""
    query = select(DataMateri)

    # Apply where conditions one at a time
    query = query.where(DataMateri.kategori == kategori)
    if detail_kategori:
        query = query.where(DataMateri.detail_kategori == detail_kategori)

    return query


@router.get("/{kategori}")
@router.get("/{kategori}/{detail_kategori}")
@cache(expire=300)  # Cache for 5 minutes
async def get_data_materi(
    kategori: str,
    detail_kategori: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    try:
        query = build_query(kategori, detail_kategori)
        result = await db.execute(query)
        data = result.scalars().all()

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
