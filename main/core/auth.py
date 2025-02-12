import os
import sys
from typing import Optional, Dict
from pathlib import Path
from fastapi import HTTPException, Header
from asgiref.sync import sync_to_async

# Get absolute paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
django_auth_path = project_root / 'django_auth'

# Configure Django settings and path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')

# Add Django app to Python path if not already there
django_auth_str = str(django_auth_path)
if django_auth_str not in sys.path:
    sys.path.insert(0, django_auth_str)

# Set other required environment variables if not already set
env_vars = {
    'DJANGO_SECRET_KEY': 'Pxf0AsnFeejnpZfp4Ya8F4wsyJcqSV2Q',
    'POSTGRES_DB': 'besb_db',
    'POSTGRES_USER': 'besb_user',
    'POSTGRES_PASSWORD': 'NsJTxYB5VY7hTN3EAulY1Ice132qKhgH',
    'POSTGRES_CONTAINER_NAME': 'besb_postgres',
    'REDIS_CONTAINER_NAME': 'besb_redis'
}

for key, value in env_vars.items():
    os.environ.setdefault(key, value)

# Initialize Django
import django
django.setup()

# Import authentication services with better error handling
try:
    from django_auth.authentication.services import verify_api_key_logic, verify_token_logic
except ImportError as e:
    # Provide more detailed error information
    import traceback
    error_msg = f"Failed to import authentication services: {str(e)}\n"
    error_msg += f"Python path: {sys.path}\n"
    error_msg += f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}"
    raise ImportError(error_msg)

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
