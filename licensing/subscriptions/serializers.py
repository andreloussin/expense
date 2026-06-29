from rest_framework import serializers
from .models import Subscription, PlanConfiguration, PlanType

class PlanConfigurationSerializer(serializers.ModelSerializer):
    plan_display = serializers.CharField(source='get_plan_type_display', read_only=True)

    class Meta:
        model = PlanConfiguration
        fields = ['plan_type', 'plan_display', 'max_devices', 'duration_days', 'price']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    remaining_slots = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = ['plan_type', 'plan_display', 'status', 'max_devices', 'remaining_slots', 'expires_at', 'is_expired']

class SubscribeRequestSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=PlanType.choices)
