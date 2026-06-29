from rest_framework import serializers
from .models import Device

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'device_id', 'registered_at']

class LicenseActivationSerializer(serializers.Serializer):
    device_id = serializers.CharField(min_length=8, max_length=8, required=True)

    def validate_device_id(self, value):
        return value.strip().upper()
