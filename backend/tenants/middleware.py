from django.db import connection
from django.core.exceptions import PermissionDenied
from .models import Tenant


class TenantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):

        request.tenant = getattr(request, "tenant", connection.tenant)

        if request.user.is_authenticated:
            tenant_id = request.headers.get(
                "X-Tenant-Id"
            )

            if tenant_id:
                try:
                    tenant = Tenant.objects.get(
                        id=tenant_id,
                        owner=request.user
                    )

                except Tenant.DoesNotExist:
                    raise PermissionDenied(
                        "Tenant invalide"
                    )

                request.tenant = tenant
                connection.set_schema(
                    tenant.schema_name
                )

            else:
                connection.set_schema_to_public()


        response = self.get_response(request)

        return response