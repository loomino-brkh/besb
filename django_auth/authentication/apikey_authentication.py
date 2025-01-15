from rest_framework import authentication, exceptions
from .apikey_models import APIKey
import hashlib
from django.utils import timezone

class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_AUTHORIZATION')
        if not api_key:
            return None
        
        try:
            prefix, key = api_key.split(' ', 1)
            if prefix.lower() != 'apikey':
                return None
        except ValueError:
            return None
        
        try:
            api_key_instance = APIKey.objects.get(hashed_key=hashlib.sha256(key.encode()).hexdigest(), revoked=False)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid or revoked API Key')
        
        if api_key_instance.expires_at and api_key_instance.expires_at < timezone.now():
            raise exceptions.AuthenticationFailed('API Key has expired')
        
        # Attach the APIKey instance to the request for permission checks
        request.api_key = api_key_instance
        
        return api_key_instance.owner, api_key_instance