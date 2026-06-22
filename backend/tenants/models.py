from django_tenants.models import TenantMixin, DomainMixin
from django.db import models


class Tenant(TenantMixin):
    name = models.CharField(
        max_length=100
    )

    created_on = models.DateField(
        auto_now_add=True
    )

    auto_create_schema = True


class Domain(DomainMixin):
    pass