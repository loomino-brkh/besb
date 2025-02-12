import os
import sys
from typing import Dict
from pathlib import Path
from fastapi import HTTPException, Header
from asgiref.sync import sync_to_async
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Get absolute paths using pathlib for better cross-platform compatibility
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
django_auth_path = project_root / 'django_auth'

# Ensure django_auth is in sys.path
if str(django_auth_path) not in sys.path:
    sys.path.insert(0, str(django_auth_path))
    sys.path.insert(0, str(project_root))

# Set Django environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
os.environ.setdefault('DJANGO_SECRET_KEY', 'Pxf0AsnFeejnpZfp4Ya8F4wsyJcqSV2Q')
os.environ.setdefault('POSTGRES_DB', 'besb_db')
os.environ.setdefault('POSTGRES_USER', 'besb_user')
os.environ.setdefault('POSTGRES_PASSWORD', 'NsJTxYB5VY7hTN3EAulY1Ice132qKhgH')
os.environ.setdefault('POSTGRES_CONTAINER_NAME', 'besb_postgres')
os.environ.setdefault('REDIS_CONTAINER_NAME', 'besb_redis')

# Initialize Django
import django
django.setup()

# Import authentication services with robust error handling
def import_auth_services():
    try:
        from django_auth.authentication.services import verify_api_key_logic, verify_token_logic
        return verify_api_key_logic, verify_token_logic
    except ImportError as e:
        logger.error(f"Failed to import authentication services: {e}")
        logger.error(f"sys.path: {sys.path}")
        logger.error(f"Current directory: {current_dir}")
        logger.error(f"Project root: {project_root}")
        logger.error(f"Django auth path: {django_auth_path}")
        raise ImportError(f"Could not import authentication services. Please check the logs for details: {e}")

verify_api_key_logic, verify_token_logic = import_auth_services()

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
