from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .apikey_models import APIKey
from .apikey_serializers import APIKeySerializer, CreateAPIKeySerializer
from .apikey_utils import get_user_api_keys, revoke_api_key

class APIKeyListView(generics.ListAPIView):
    serializer_class = APIKeySerializer
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        return get_user_api_keys(self.request.user)

class APIKeyCreateView(generics.CreateAPIView):
    serializer_class = CreateAPIKeySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        api_key_instance = serializer.save()

class APIKeyRevokeView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    queryset = APIKey.objects.all()
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        success = revoke_api_key(instance.pk, self.request.user)
        if not success:
            raise NotFound("API Key not found.") 
