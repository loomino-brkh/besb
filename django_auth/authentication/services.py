from rest_framework_simplejwt.tokens import AccessToken
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError

def verify_token_logic(token: str) -> dict:
    """
    Core logic for verifying a JWT token.
    Returns a dictionary with validation results.
    """
    try:
        token_obj = AccessToken(token)
        user_id = token_obj['user_id']
        
        # Check if result is cached
        cache_key = f'token_valid_{user_id}'
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return {
                'valid': True,
                'cached': True,
                'user_id': user_id
            }

        # Verify user exists
        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
        if not user:
            return {
                'valid': False,
                'error': 'User not found'
            }

        # Cache the successful verification
        cache.set(cache_key, True, timeout=300)  # Cache for 5 minutes
        
        return {
            'valid': True,
            'cached': False,
            'user_id': user_id
        }

    except TokenError:
        return {
            'valid': False,
            'error': 'Invalid token'
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def verify_api_key_logic(api_key: str) -> dict:
    """
    Core logic for verifying an API key.
    Returns a dictionary with validation results.
    """
    from .models import APIKey  # Import here to avoid circular imports
    
    try:
        # Check if result is cached
        cache_key = f'api_key_valid_{api_key[:32]}'  # Use first 32 chars of key as cache key
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return {
                'valid': True,
                'cached': True,
                'permission': cached_result['permission']
            }

        # Check if API key exists and is valid
        api_key_obj = APIKey.objects.filter(key=api_key, is_active=True).first()
        if not api_key_obj:
            return {
                'valid': False,
                'error': 'Invalid or inactive API key'
            }

        # Cache the successful verification
        result = {
            'valid': True,
            'permission': api_key_obj.permission,
            'key_id': api_key_obj.id
        }
        cache.set(cache_key, result, timeout=300)  # Cache for 5 minutes
        
        return result

    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }
