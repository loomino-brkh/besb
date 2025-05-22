from typing import Any, Optional, cast

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .apikey_models import APIKey
from .apikey_serializers import APIKeySerializer, CreateAPIKeySerializer
from .apikey_utils import get_user_api_keys, revoke_api_key
from .permissions import LocalhostOnly

User = get_user_model()


class APIKeyListView(generics.ListAPIView):  # type: ignore[generic]
    serializer_class = APIKeySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[APIKey]:
        return get_user_api_keys(cast(User, self.request.user))  # type: ignore[arg-type]


class APIKeyCreateView(generics.CreateAPIView):  # type: ignore[generic]
    serializer_class = CreateAPIKeySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:  # type: ignore[override]
        serializer.save()  # Removed unused variable


class APIKeyRevokeView(generics.DestroyAPIView):  # type: ignore[generic]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = APIKey.objects.all()
    lookup_field = "pk"

    def perform_destroy(self, instance: Any) -> None:  # type: ignore[override]
        success = revoke_api_key(instance.pk, cast(User, self.request.user))  # type: ignore[arg-type]
        if not success:
            raise NotFound("API Key not found.")


class APIKeyVerifyView(APIView):
    permission_classes = [LocalhostOnly]

    def post(self, request: Request) -> Response:
        api_key: Optional[str] = request.data.get("api_key")
        if not api_key:
            return Response(
                {"error": "API key is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = APIKey.authenticate(api_key)
        if not user:
            return Response(
                {"valid": False, "message": "Invalid or expired API key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Assuming hash_key is a static method that takes a key parameter
            api_key_obj = APIKey.objects.get(hashed_key=APIKey.hash_key(key=api_key))  # type: ignore[arg-type]
            return Response(
                {
                    "valid": True,
                    "owner": user.username,
                    "name": api_key_obj.name,
                    "permission": api_key_obj.permission,
                    "expires_at": api_key_obj.expires_at,
                    "allowed_endpoint": api_key_obj.allowed_endpoint,
                }
            )
        except APIKey.DoesNotExist:
            return Response(
                {"valid": False, "message": "Invalid API key"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
