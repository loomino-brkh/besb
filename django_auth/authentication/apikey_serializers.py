import logging
from typing import Any, Dict

from rest_framework import serializers

from .apikey_models import APIKey
from .apikey_utils import create_api_key

logger = logging.getLogger(__name__)


class APIKeySerializer(serializers.ModelSerializer[APIKey]):
    class Meta:  # type: ignore[override]
        model = APIKey
        fields = [
            "id",
            "name",
            "key",
            "created_at",
            "expires_at",
            "revoked",
            "permission",
        ]


class CreateAPIKeySerializer(serializers.ModelSerializer[APIKey]):
    expires_in_days = serializers.IntegerField(write_only=True, required=False)
    PERMISSION_CHOICES = (
        ("read_only", "Read Only"),
        ("write_only", "Write Only"),
        ("read_write", "Read and Write"),
    )
    permission = serializers.ChoiceField(
        choices=PERMISSION_CHOICES, write_only=True, required=True
    )

    class Meta:  # type: ignore[override]
        model = APIKey
        fields = ["name", "expires_in_days", "permission"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            logger.error("Authentication credentials missing or invalid.")
            raise serializers.ValidationError(
                "Authentication credentials were not provided or are invalid."
            )
        return attrs

    def validate_permission(self, value: str) -> str:
        allowed_permissions = [choice[0] for choice in self.PERMISSION_CHOICES]
        if value not in allowed_permissions:
            raise serializers.ValidationError(
                f"Permission must be one of {allowed_permissions}."
            )
        return value

    def create(self, validated_data: Dict[str, Any]) -> APIKey:
        try:
            expires_in_days = validated_data.pop("expires_in_days", None)
            permission = validated_data.pop("permission")
            api_key = create_api_key(
                self.context["request"].user,
                validated_data["name"],
                expires_in_days,
                permission=permission,
            )
            return api_key
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            raise serializers.ValidationError(
                "An error occurred while creating the API key."
            )
