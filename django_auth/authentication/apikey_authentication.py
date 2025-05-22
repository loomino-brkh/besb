import hashlib
from typing import Optional, Tuple

from django.contrib.auth.models import User  # For proper typing
from django.utils import timezone
from rest_framework import authentication, exceptions
from rest_framework.request import Request

from .apikey_models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[User, APIKey]]:
        api_key: Optional[str] = request.META.get("HTTP_AUTHORIZATION")
        if not api_key:
            return None

        try:
            prefix: str
            key: str
            prefix, key = api_key.split(" ", 1)
            if prefix.lower() != "apikey":
                return None
        except ValueError:
            return None

        try:
            api_key_instance: APIKey = APIKey.objects.get(
                hashed_key=hashlib.sha256(key.encode()).hexdigest(), revoked=False
            )
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid or revoked API Key")

        if api_key_instance.expires_at and api_key_instance.expires_at < timezone.now():
            raise exceptions.AuthenticationFailed("API Key has expired")

        # Attach the APIKey instance to the request for permission checks
        setattr(request, "api_key", api_key_instance)

        return api_key_instance.owner, api_key_instance
