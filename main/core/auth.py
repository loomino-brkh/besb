from fastapi import HTTPException, Header
from typing import Optional, Dict
import os
import sys

# Add django_auth directory to Python path
django_auth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'django_auth'))
sys.path.append(django_auth_path)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_auth.auth_project.settings')
django.setup()

# Import Django verification logic
from asgiref.sync import sync_to_async
from django_auth.authentication.services import verify_api_key_logic, verify_token_logic

async def verify_api_key(authorization: str = Header(None)) -> Dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="No API key provided")

    if not authorization.startswith("ApiKey "):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    api_key = authorization.split(" ")[1]
    try:
        result = await sync_to_async(verify_api_key_logic)(api_key)
        if not result.get('valid', False):
            raise HTTPException(
                status_code=401,
                detail=f"Invalid API key: {result.get('error', 'Unknown error')}"
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Authentication service error: {str(e)}"
        )

async def verify_token(authorization: str = Header(None)) -> Dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization provided")

    auth_parts = authorization.split()
    if len(auth_parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    auth_type = auth_parts[0].lower()
    
    if auth_type == "bearer":
        token = auth_parts[1]
        try:
            result = await sync_to_async(verify_token_logic)(token)
            if not result.get('valid', False):
                raise HTTPException(
                    status_code=401,
                    detail=f"Invalid token: {result.get('error', 'Unknown error')}"
                )
            # For Bearer tokens, we grant full permissions
            result["permission"] = "read_write"
            return result
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Authentication service error: {str(e)}"
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
