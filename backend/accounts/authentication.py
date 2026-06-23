from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import connection

class TenantJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result

        if hasattr(user, "tenant"):
            tenant = user.tenant
            request.tenant = tenant
            connection.set_schema(
                tenant.schema_name
            )

        else:
            connection.set_schema_to_public()

        return user, token