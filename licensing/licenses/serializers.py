from rest_framework import serializers
from .models import License, MachineActivation

class ActivationSerializer(serializers.Serializer):
    license_key = serializers.UUIDField()
    machine_id = serializers.CharField()

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineActivation
        fields =  [
            "machine_id",
            "activated_at",
            "last_check",
            "is_revoked",
        ]

class LicenseDetailSerializer(serializers.ModelSerializer):
    active_machines = serializers.SerializerMethodField()
    revoked_machines = serializers.SerializerMethodField()

    class Meta:
        model = License
        fields = [
            "key",
            "expires_at",
            "max_devices",
            "active",
            "created_at",
            "active_machines",
            "revoked_machines",
        ]

    def get_active_machines(self, obj):
        machines = obj.machines.filter(
            is_revoked=False
        )

        return MachineSerializer(
            machines,
            many=True
        ).data

    def get_revoked_machines(self, obj):
        machines = obj.machines.filter(
            is_revoked=True
        )

        return MachineSerializer(
            machines,
            many=True
        ).data
        
class LicenseListSerializer(serializers.ModelSerializer):
    active_devices_count = serializers.SerializerMethodField()

    class Meta:
        model = License
        fields = [
            "key",
            "expires_at",
            "max_devices",
            "active",
            "created_at",
            "active_devices_count",
        ]
    
    def get_active_devices_count(self, obj):
        return obj.machines.filter(
            is_revoked=False
        ).count()