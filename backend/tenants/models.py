from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Tenant(TenantMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tenant',
        null=True,
        blank=True
    )

    auto_create_schema = True


class Domain(DomainMixin):
    pass