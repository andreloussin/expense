from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Tenant(TenantMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tenants',
    )

    name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    auto_create_schema = True
    
    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass