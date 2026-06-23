from django.contrib.auth.models import User
from rest_framework import serializers
from tenants.models import Tenant
import uuid
from django.db import connection, transaction

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password"
        ]

    @transaction.atomic
    def create(self, validated_data):

        print("SCHEMA AVANT USER:", connection.schema_name)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        print("SCHEMA APRES USER:", connection.schema_name) 
        
        Tenant.objects.create(
            user=user,
            schema_name=f"tenant_{uuid.uuid4().hex[:8]}"
        )
        
        print("SCHEMA APRES TENANT:", connection.schema_name)

        return user