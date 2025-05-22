import binascii
import os
from datetime import timedelta
from typing import Optional, Union

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserType  # For type annotations
from django.utils import timezone

from .apikey_models import APIKey

User = get_user_model()


def generate_unique_key() -> str:
    return binascii.hexlify(os.urandom(32)).decode()


def create_api_key(
    user: UserType,
    name: str,
    expires_in_days: Optional[int] = None,
    permission: str = "read_write",
) -> APIKey:
    api_key = APIKey.objects.create(owner=user, name=name, permission=permission)
    if expires_in_days:
        api_key.expires_at = timezone.now() + timedelta(days=expires_in_days)
        api_key.save()
    return api_key


def revoke_api_key(api_key_id: Union[int, str], user: UserType) -> bool:
    try:
        api_key = APIKey.objects.get(id=api_key_id)
        if api_key.owner != user:
            return False
        api_key.revoked = True
        api_key.save()
        return True
    except APIKey.DoesNotExist:
        return False


def get_user_api_keys(user: UserType):
    return APIKey.objects.filter(owner=user, revoked=False)
