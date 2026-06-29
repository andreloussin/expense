import json
import base64
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from subscriptions.models import Subscription, SubscriptionStatus
from .models import Device
from .serializers import LicenseActivationSerializer, DeviceSerializer
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def generate_signed_license_key(payload_data):
    private_key_pem = getattr(settings, "RSA_PRIVATE_KEY").encode('utf-8')
    private_key = load_pem_private_key(private_key_pem, password=None)
    data_string = json.dumps(payload_data, separators=(',', ':'))
    
    signature = private_key.sign(
        data_string.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    full_license = {
        "data": payload_data,
        "sig": base64.b64encode(signature).decode('utf-8')
    }
    return base64.urlsafe_b64encode(json.dumps(full_license).encode('utf-8')).decode('utf-8').rstrip('=')

class DeviceManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtenir la liste globale des devices de l'utilisateur"""
        devices = request.user.devices.all()
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Enregistrer/Associer uniquement une nouvelle device au compte utilisateur"""
        serializer = LicenseActivationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 1. Trouver l'abonnement EN COURS de validité via la propriété du User
        subscription = request.user.active_subscription

        if not subscription:
            return Response(
                {"error": "Aucun abonnement valide ou actif trouvé pour enregistrer un appareil."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        device_id = serializer.validated_data['device_id'].strip().upper()

        # 2. Vérifier si la device est DÉJÀ enregistrée globalement pour cet utilisateur
        device_exists = request.user.devices.filter(device_id=device_id).exists()

        if device_exists:
            return Response(
                {"message": "Cette device est déjà associée à votre compte.", "device_id": device_id}, 
                status=status.HTTP_200_OK
            )

        # 3. Si c'est une nouvelle device, vérification stricte des quotas globaux
        if request.user.remaining_slots <= 0:
            return Response({
                "error": f"Limite d'appareils atteinte. Votre plan autorise {subscription.max_devices} device(s) au total."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 4. Enregistrement global de la device
        Device.objects.create(user=request.user, device_id=device_id)
        
        # 5. Générer le payload avec les informations de l'abonnement à jour
        payload = {
            "email": request.user.email,
            "mid": device_id,
            "exp": subscription.expires_at.strftime('%Y-%m-%d'),
            "plan": subscription.plan_type
        }
        license_key = generate_signed_license_key(payload)

        return Response({
            "message": "device associée avec succès à votre compte.",
            "device_id": device_id,
            "license_key": license_key
        }, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """Supprimer une device globalement pour libérer un slot"""
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response({"error": "device_id manquant."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            device = request.user.devices.get(device_id=device_id.upper())
            device.delete()
            return Response({"message": "device supprimée. Un emplacement a été libéré."}, status=status.HTTP_200_OK)
        except Device.DoesNotExist:
            return Response({"error": "device introuvable."}, status=status.HTTP_404_NOT_FOUND)


class RedownloadLicenseView(APIView):
    """
    Endpoint pour récupérer à nouveau la licence d'une device déjà enregistrée.
    Utile lors d'un renouvellement ou si l'utilisateur a perdu son fichier/string.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, device_id):
        # 1. Nettoyer le device_id passé dans l'URL
        device_id = device_id.strip().upper()

        # 2. Vérifier si l'utilisateur possède un abonnement actif/valide
        subscription = request.user.active_subscription
        if not subscription:
            return Response(
                {"error": "Aucun abonnement valide ou actif trouvé pour régénérer la licence."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. Vérifier si la device appartient bien à cet utilisateur
        device_exists = request.user.devices.filter(device_id=device_id).exists()
        if not device_exists:
            return Response(
                {"error": "Cette device n'est pas enregistrée sur votre compte. Veuillez l'ajouter d'abord."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # 4. Régénérer le payload avec les informations de l'abonnement à jour
        payload = {
            "email": request.user.email,
            "mid": device_id,
            "exp": subscription.expires_at.strftime('%Y-%m-%d'),
            "plan": subscription.plan_type
        }

        # 5. Signer cryptographiquement la nouvelle licence
        try:
            license_key = generate_signed_license_key(payload)
            return Response({
                "message": "Licence récupérée avec succès.",
                "device_id": device_id,
                "license_key": license_key
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error": "Erreur lors de la signature cryptographique de la licence."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )