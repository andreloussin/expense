from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import connection
from tenants.models import Tenant
from rest_framework.exceptions import AuthenticationFailed

class TenantJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result

        tenant_id = request.headers.get(
            "X-Tenant-Id"
        )
        
        if tenant_id:
            try:
                tenant = Tenant.objects.get(
                    id=tenant_id,
                    user=user,
                    is_active=True
                )
            except Tenant.DoesNotExist:
                raise AuthenticationFailed(
                    "Tenant invalide"
                )
            request.tenant = tenant
            connection.set_schema(
                tenant.schema_name
            )
        else:
            connection.set_schema_to_public()

        return user, token