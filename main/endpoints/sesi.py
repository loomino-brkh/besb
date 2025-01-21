from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List

from core.db import get_async_db
from schema.sesi_schema import Sesi

router = APIRouter()

@router.get("/{acara}")
async def get_sesi_by_acara(
    acara: str,
    db=Depends(get_async_db)
):
    query = select(Sesi.sesi).where(Sesi.acara == acara)
    
    try:
        result = await db.execute(query)
        data = result.all()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No sesi found for acara: {acara}")
        
        # Convert result into list of sesi
        return [{"sesi": item[0]} for item in data]
        
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