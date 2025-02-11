from django.db import models
import uuid

class APIKey(models.Model):
    """Model for storing API keys"""
    PERMISSION_CHOICES = [
        ('read_only', 'Read Only'),
        ('write_only', 'Write Only'),
        ('read_write', 'Read and Write'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=50)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='read_only')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['key']),
        ]
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f"{self.name} ({self.permission})"

    def save(self, *args, **kwargs):
        # Generate a random API key if not set
        if not self.key:
            self.key = uuid.uuid4().hex
        super().save(*args, **kwargs)
