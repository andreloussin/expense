from django.db import connection
from django_tenants.middleware import BaseTenantMiddleware
from django_tenants.utils import get_tenant_model, get_public_schema_name


class UserTenantMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self,request):
        if request.user.is_authenticated:
            tenant=request.user.usertenant.tenant
            connection.set_schema(
                tenant.schema_name
            )

        response=self.get_response(request)

        return response
    

class UserJWTTenantMiddleware(BaseTenantMiddleware):
    def process_request(self, request):
        tenant_model = get_tenant_model()
        public_schema = get_public_schema_name()
        
        # Par défaut, on initialise sur le schéma public (nécessaire pour que l'auth fonctionne)
        tenant = tenant_model.objects.get(schema_name=public_schema)
        
        # Si l'utilisateur est authentifié par SimpleJWT (les middlewares précédents ont fait le travail)
        if hasattr(request, 'user') and request.user.is_authenticated:
            # On vérifie s'il est lié à un tenant
            if getattr(request.user, 'tenant', None):
                tenant = request.user.tenant

        # On applique le tenant à la requête et à la connexion PostgreSQL
        request.tenant = tenant
        self.setup_url_routing(request)