# tenants/serializers.py

from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tenant

        fields = [
            "id",
            "name",
            "is_active",
            "schema_name"
        ]

        read_only_fields = [
            "id",
            "schema_name",
            "is_active"
        ]