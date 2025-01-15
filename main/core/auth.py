from fastapi import HTTPException, Header, Depends
from typing import Optional
import os
import httpx
import hashlib

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8001/auth/verify/",
                headers={
                    "Authorization": authorization,
                    "Host": f"localhost"
                }
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid token: {response.text}"
                )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Authentication service unavailable: {str(e)}"
        )
