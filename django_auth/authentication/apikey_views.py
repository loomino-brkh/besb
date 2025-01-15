from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .permissions import LocalhostOnly
from rest_framework.response import Response
from rest_framework.views import APIView
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

class APIKeyVerifyView(APIView):
    def post(self, request):
        api_key = request.data.get('api_key')
        if not api_key:
            return Response(
                {"error": "API key is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = APIKey.authenticate(api_key)
        if not user:
            return Response(
                {"valid": False, "message": "Invalid or expired API key"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            api_key_obj = APIKey.objects.get(hashed_key=APIKey.hash_key(APIKey, api_key))
            return Response({
                "valid": True,
                "owner": user.username,
                "name": api_key_obj.name,
                "permission": api_key_obj.permission,
                "expires_at": api_key_obj.expires_at,
                "allowed_endpoint": api_key_obj.allowed_endpoint
            })
        except APIKey.DoesNotExist:
            return Response(
                {"valid": False, "message": "Invalid API key"},
                status=status.HTTP_401_UNAUTHORIZED
            )
