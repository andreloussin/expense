from django.urls import path
from .views import DeviceManagerView, RedownloadLicenseView

urlpatterns = [
    # Route principale : GET (lister), POST (ajouter/activer), DELETE (supprimer via ?device_id=...)
    path('', DeviceManagerView.as_view(), name='devices'),
    
    # Route pour récupérer la licence d'une device existante
    # Exemple d'appel : /api/devices/A4F8E29D/license/
    path('<str:device_id>/license/', RedownloadLicenseView.as_view(), name='devices.license'),
]
