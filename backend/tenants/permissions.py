from rest_framework.permissions import BasePermission

class HasTenant(BasePermission):
    def has_permission(
        self,
        request,
        view
    ):
        return hasattr(
            request,
            "tenant"
        )
        
class IsTenantOwner(BasePermission):
    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return obj.user == request.user
    
class IsTenantActive(BasePermission):
    def has_permission(self, request, view):
        tenant = getattr(
            request,
            "tenant",
            None
        )

        if not tenant:
            return False

        if view.action in [
            "create",
            "update",
            "partial_update",
            "destroy"
        ]:
            return tenant.is_active

        return True