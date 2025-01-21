from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi_cache.decorator import cache
from fastapi_limiter.depends import RateLimiter
from sqlmodel import Session, select
from typing import Optional

from core.auth import verify_token
from core.db import get_db_dependency
from schema.url_schema import URL, URLCreate, URLResponse

router = APIRouter()

@router.get("/{code}")
@cache(expire=300)  # Cache for 5 minutes
async def get_url(
    code: str,
    session: Session = Depends(get_db_dependency)
) -> Optional[URLResponse]:
    """Get the original URL for a given code."""
    statement = select(URL).where(URL.url_code == code)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="URL not found")
    return URLResponse(url=result.url, url_code=result.url_code)

@router.post("/")
def create_url(
    url: str = Form(...),
    session: Session = Depends(get_db_dependency),
    _: str = Depends(verify_token),
    _rate_limit: Optional[None] = Depends(RateLimiter(times=10, minutes=1))  # 10 requests per minute
) -> URLResponse:
    """Create a new shortened URL using form data."""
    db_url = URL(url=url)
    session.add(db_url)
    return URLResponse(url=db_url.url, url_code=db_url.url_code)