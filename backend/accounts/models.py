from django.contrib.auth.models import User
from tenants.models import Tenant
from django.db import models


class UserTenant(models.Model):
    user=models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    tenant=models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE
    )