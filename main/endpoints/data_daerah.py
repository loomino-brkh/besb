from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List

from core.db import get_async_db
from schema.data_daerah_schema import DataDaerah

router = APIRouter()

@router.get("/{daerah}")
async def get_data_by_daerah(
    daerah: str,
    db=Depends(get_async_db)
):
    query = select(DataDaerah.ranah, DataDaerah.detail_ranah).where(DataDaerah.daerah == daerah)
    
    try:
        result = await db.execute(query)
        data = result.all()
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for daerah: {daerah}")
        
        # Convert result into list of dictionaries with only ranah and detail_ranah
        return [{"ranah": item[0], "detail_ranah": item[1]} for item in data]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")