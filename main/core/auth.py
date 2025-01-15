from fastapi import HTTPException, Header, Depends
from typing import Optional
import os
import httpx
import hashlib

async def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No API key provided")

    if not authorization.startswith("ApiKey "):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    api_key = authorization.split(" ")[1]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8001/auth/apikeys/verify/",
                json={"api_key": api_key},
                headers={"Host": "localhost"}
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid API key: {response.text}"
                )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Authentication service unavailable: {str(e)}"
        )

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization provided")

    # Check if it's a Bearer token or API key
    auth_parts = authorization.split()
    if len(auth_parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    auth_type = auth_parts[0].lower()
    
    if auth_type == "bearer":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:8001/auth/verify/",
                    headers={
                        "Authorization": authorization,
                        "Host": "localhost"
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
    elif auth_type == "apikey":
        return await verify_api_key(authorization)
    else:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authorization type. Use 'Bearer' or 'ApiKey'"
        )

async def verify_auth(authorization: str = Header(None)):
    """Combined authentication that accepts either token or API key"""
    return await verify_token(authorization)
