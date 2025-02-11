from fastapi import HTTPException, Header, Depends
from typing import Optional, Dict
import os
import hashlib
from . import auth_service  # Import the local auth_service module

async def verify_api_key(authorization: str = Header(None)) -> Dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="No API key provided")

    if not authorization.startswith("ApiKey "):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    api_key = authorization.split(" ")[1]
    try:
        # Call the local verify_api_key function
        result = auth_service.verify_api_key(api_key)
        if not result:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid API key"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Authentication service unavailable: {str(e)}"
        )

async def verify_token(authorization: str = Header(None)) -> Dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization provided")

    # Check if it's a Bearer token or API key
    auth_parts = authorization.split()
    if len(auth_parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    auth_type = auth_parts[0].lower()
    
    if auth_type == "bearer":
        try:
            # Call the local verify_token function
            result = auth_service.verify_token(authorization)
            if not result:
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid token"
                )
            # For Bearer tokens, we grant full permissions
            result["permission"] = "read_write"
            return result
        except Exception as e:
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

async def verify_read_permission(authorization: str = Header(None)) -> Dict:
    """Verifies if the token/key has read permission"""
    auth_data = await verify_token(authorization)
    permission = auth_data.get("permission", "")
    
    if permission not in ["read_only", "read_write"]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Read access required."
        )
    return auth_data

async def verify_write_permission(authorization: str = Header(None)) -> Dict:
    """Verifies if the token/key has write permission"""
    auth_data = await verify_token(authorization)
    permission = auth_data.get("permission", "")
    
    if permission not in ["write_only", "read_write"]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Write access required."
        )
    return auth_data
