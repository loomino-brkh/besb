from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

# from typing import List
from fastapi_cache.decorator import cache

from core.db import get_async_db
from schema.data_daerah_schema import DataDaerah

router = APIRouter()


@router.get("/{daerah}")
# @cache(expire=300)  # Cache results for 5 minutes
async def get_data_by_daerah(daerah: str, db=Depends(get_async_db)):
    query = select(DataDaerah.ranah, DataDaerah.detail_ranah).where(
        DataDaerah.daerah == daerah
    )

    try:
        result = await db.execute(query)
        data = result.all()

        if not data:
            raise HTTPException(
                status_code=404, detail=f"No data found for daerah: {daerah}"
            )

        # Convert result into list of dictionaries with only ranah and detail_ranah
        return [{"ranah": item[0], "detail_ranah": item[1]} for item in data]

    except HTTPException:
        raise
    except Exception as e:
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
