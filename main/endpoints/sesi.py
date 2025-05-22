from core.db import get_async_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from schema.sesi_schema import Sesi
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get("/{acara}")
@cache(expire=300)  # Cache for 5 minutes
async def get_sesi_by_acara(acara: str, db: AsyncSession = Depends(get_async_db)):
    query = select(Sesi).where(Sesi.acara == acara)
    # Although diagnostics might suggest `exec`, runtime errors indicate `execute` is needed
    # in this environment for AsyncSession.
    try:
        result = await db.execute(query)  # type: ignore
        data = result.scalars().all()

        if not data:
            raise HTTPException(
                status_code=404, detail=f"No sesi found for acara: {acara}"
            )

        # Convert result into list of sesi with waktu
        return [
            {
                "sesi": item.sesi,
                "waktu": item.waktu.strftime("%H:%M") if item.waktu else None,
            }
            for item in data
        ]

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
