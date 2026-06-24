import uuid

from rest_framework import viewsets
from .models import Tenant
from .serializers import TenantSerializer
from .permissions import IsTenantOwner
from rest_framework.permissions import IsAuthenticated


class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):
        
        return Tenant.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            schema_name=f"tenant_{uuid.uuid4().hex[:8]}"
        )