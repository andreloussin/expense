from django.db import models
from django.conf import settings
import uuid


class License(models.Model):
    key = models.UUIDField(
        default=uuid.uuid4,
        unique=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="licenses"
    )

    expires_at = models.DateTimeField()
    max_devices = models.IntegerField(default=1)

    active = models.BooleanField(default=True)
    
    schema_version = models.PositiveIntegerField(default=1)
    signature = models.TextField(blank=True, null=True)  # RSA later

    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        from django.utils import timezone
        return self.active and self.expires_at > timezone.now()

    def __str__(self):

        return str(self.key)


class MachineActivation(models.Model):
    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name="machines"
    )

    machine_id = models.CharField(
        max_length=128
    )

    activated_at = models.DateTimeField(auto_now_add=True)
    last_check = models.DateTimeField(auto_now=True)
    
    is_revoked = models.BooleanField(default=False)

    class Meta:

        unique_together = (
            "license",
            "machine_id"
        )