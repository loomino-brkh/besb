from typing import Any, Dict, List

from core.db import get_async_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from schema.data_hobi_schema import DataHobi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
@cache(expire=300)  # Cache for 5 minutes
async def get_hobi_data(
    db: AsyncSession = Depends(get_async_db),
) -> List[Dict[str, Any]]:
    """Get all hobbies data"""
    try:
        query = select(DataHobi)
        result = await db.execute(query)
        data = result.scalars().all()

        if not data:
            return []

        return [{"kategori": item.kategori, "hobi": item.hobi} for item in data]
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
