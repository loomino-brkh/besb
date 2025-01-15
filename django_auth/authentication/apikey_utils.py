import binascii
import os
from .apikey_models import APIKey
from django.utils import timezone

def generate_unique_key():
    return binascii.hexlify(os.urandom(32)).decode()

def create_api_key(user, name, expires_in_days=None, permission='read_write'):
    api_key = APIKey.objects.create(
        owner=user,
        name=name,
        permission=permission
    )
    if expires_in_days:
        api_key.expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        api_key.save()
    return api_key

def revoke_api_key(api_key_id, user):
    try:
        api_key = APIKey.objects.get(id=api_key_id)
        if api_key.owner != user:
            return False
        api_key.revoked = True
        api_key.save()
        return True
    except APIKey.DoesNotExist:
        return False

def get_user_api_keys(user):
    return APIKey.objects.filter(owner=user, revoked=False)
