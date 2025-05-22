import hashlib
from typing import Any, TypedDict, cast

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .apikey_models import APIKey

UserModel = get_user_model()


class TokenVerificationResult(TypedDict, total=False):
    valid: bool
    cached: bool
    user_id: int
    error: str


class APIKeyVerificationResult(TypedDict, total=False):
    valid: bool
    permission: str
    owner_id: int
    key_id: int
    error: str


def verify_token_logic(raw_token: str) -> TokenVerificationResult:
    """
    Core logic for verifying a JWT token.
    Returns a dictionary with validation results.
    """
    try:
        # Handle token initialization directly
        token_obj = AccessToken(raw_token)  # type: ignore
        user_id = int(token_obj["user_id"])  # Ensure user_id is an int

        # Check if result is cached
        cache_key = f"token_valid_{user_id}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return {"valid": True, "cached": True, "user_id": user_id}

        # Verify user exists
        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
        if not user:
            return {"valid": False, "error": "User not found"}
        user_id = int(cast(Any, user).id)  # Convert to int explicitly with type cast

        # Cache the successful verification
        cache.set(cache_key, True, timeout=300)  # Cache for 5 minutes

        return {"valid": True, "cached": False, "user_id": user_id}

    except TokenError:
        return {"valid": False, "error": "Invalid token"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def verify_api_key_logic(api_key: str) -> APIKeyVerificationResult:
    """
    Core logic for verifying an API key.
    Uses the APIKey model's authenticate method and checks expiration/revocation.
    Returns a dictionary with validation results.
    """
    try:
        # Check if result is cached
        cache_key = f"api_key_valid_{hashlib.sha256(api_key.encode()).hexdigest()}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cast(APIKeyVerificationResult, cached_result)

        # Authenticate using the model's method
        owner = APIKey.authenticate(api_key)
        if not owner:
            return {"valid": False, "error": "Invalid or expired API key"}

        # Get the API key object for additional checks
        hashed = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_obj = APIKey.objects.get(hashed_key=hashed, revoked=False)

        # Check expiration
        if api_key_obj.expires_at and api_key_obj.expires_at < timezone.now():
            return {"valid": False, "error": "API key has expired"}

        # Cache and return successful result
        result: APIKeyVerificationResult = {
            "valid": True,
            "permission": api_key_obj.permission,
            "owner_id": int(cast(Any, owner).id),
            "key_id": int(cast(Any, api_key_obj).id),
        }
        cache.set(cache_key, result, timeout=300)  # Cache for 5 minutes

        return result

    except APIKey.DoesNotExist:
        return {"valid": False, "error": "Invalid API key"}
    except Exception as e:
        return {"valid": False, "error": str(e)}
