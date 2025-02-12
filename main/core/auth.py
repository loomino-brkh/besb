import os
import sys
from typing import Dict
from pathlib import Path
from fastapi import HTTPException, Header
from asgiref.sync import sync_to_async
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configure environment variables first
os.environ['DJANGO_SECRET_KEY'] = 'Pxf0AsnFeejnpZfp4Ya8F4wsyJcqSV2Q'
os.environ['DJANGO_SETTINGS_MODULE'] = 'auth_project.settings'
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

# Configure Django environment
project_root = '/app'  # Container root directory
django_auth_path = os.path.join(project_root, 'django_auth')

# Configure Python paths for import resolution
local_auth_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'django_auth')
container_auth_path = django_auth_path

# Add both local and container paths for IDE and runtime resolution
for path in [local_auth_path, container_auth_path]:
    if path not in sys.path:
        sys.path.insert(0, path)
        sys.path.insert(0, os.path.dirname(path))

logger.info(f"Python paths configured:")
logger.info(f"Local auth path: {local_auth_path}")
logger.info(f"Container auth path: {container_auth_path}")
logger.info(f"sys.path: {sys.path}")

# Configure remaining environment variables
os.environ.setdefault('POSTGRES_DB', 'besb_db')
os.environ.setdefault('POSTGRES_USER', 'besb_user')
os.environ.setdefault('POSTGRES_PASSWORD', 'NsJTxYB5VY7hTN3EAulY1Ice132qKhgH')
os.environ.setdefault('POSTGRES_CONTAINER_NAME', 'besb_postgres')
os.environ.setdefault('REDIS_CONTAINER_NAME', 'besb_redis')

# Initialize Django
import django
django.setup()

# Import authentication services
logger.info("Attempting to import authentication services...")
try:
    from authentication import services  # type: ignore
    verify_api_key_logic = services.verify_api_key_logic
    verify_token_logic = services.verify_token_logic
    logger.info("Successfully imported authentication services")
except ImportError as e:
    logger.error(f"Failed to import authentication services: {e}")
    logger.error(f"sys.path: {sys.path}")
    raise ImportError(f"Could not import authentication services: {e}")

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
