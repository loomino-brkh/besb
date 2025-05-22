import binascii
import hashlib
import os
from datetime import timedelta
from typing import Any, Optional

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class APIKey(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text="A label for the API key.")
    key = models.CharField(max_length=64, unique=True, editable=False)
    hashed_key = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    permission = models.CharField(
        max_length=20,
        choices=[
            ("read_only", "Read Only"),
            ("write_only", "Write Only"),
            ("read_write", "Read and Write"),
        ],
        default="read_write",
    )
    allowed_endpoint = models.CharField(
        max_length=255,
        help_text="Endpoint this API key is allowed to access",
        null=True,
        blank=True,
    )
    used = models.BooleanField(default=False)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.key:
            self.key = self.generate_api_key()
            self.hashed_key = self.hash_key(self.key)
        expires_in_days: Optional[int] = kwargs.pop("expires_in_days", None)
        if expires_in_days:
            self.expires_at = timezone.now() + timedelta(days=expires_in_days)
        super().save(*args, **kwargs)

    def generate_api_key(self) -> str:
        return binascii.hexlify(os.urandom(32)).decode()

    def hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def authenticate(cls, key: str) -> Optional[User]:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        try:
            api_key = cls.objects.get(hashed_key=hashed, revoked=False)
            if api_key.expires_at and api_key.expires_at < timezone.now():
                return None
            return api_key.owner
        except cls.DoesNotExist:
            return None

    def __str__(self) -> str:
        return f"{self.name} - {'Revoked' if self.revoked else 'Active'}"
