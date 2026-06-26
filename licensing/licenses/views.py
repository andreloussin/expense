from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import License, MachineActivation
from .serializers import ActivationSerializer, LicenseListSerializer, LicenseDetailSerializer


class ActivateView(APIView):

    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        license_key = serializer.validated_data["license_key"]
        machine_id = serializer.validated_data["machine_id"]

        # 🔍 license check
        try:
            license = License.objects.get(key=license_key, active=True)
        except License.DoesNotExist:
            return Response({"error": "Invalid license"}, status=400)

        # ⛔ expiration
        if not license.is_valid():
            return Response({"error": "License expired"}, status=403)

        # 🚫 device limit
        active_devices = MachineActivation.objects.filter(
            license=license,
            is_revoked=False
        ).count()

        if active_devices >= license.max_devices:
            return Response({"error": "Device limit reached"}, status=403)

        # 🔥 machine exists
        activation = MachineActivation.objects.filter(
            license=license,
            machine_id=machine_id
        ).first()

        # ❌ IMPORTANT RULE: revoked machine can NEVER auto-reactivate
        if activation and activation.is_revoked:
            return Response(
                {"error": "Machine revoked"},
                status=403
            )

        # ✔ already active
        if activation:
            activation.last_check = timezone.now()
            activation.save()

            return Response({"status": "already_active"})

        # ✅ create new activation
        MachineActivation.objects.create(
            license=license,
            machine_id=machine_id
        )
        
        return Response({
            "status": "activated",
            "expires_at": license.expires_at,
        })

class CreateLicenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # 🧠 BUSINESS RULES (IMPORTANT)
        # ex: 1 free license max
        existing = License.objects.filter(user=user, active=True).count()

        if existing >= 1:
            return Response(
                {"error": "You already have an active license"},
                status=403
            )

        license = License.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(days=30),
            max_devices=2,
            active=True
        )

        return Response({
            "license_key": str(license.key),
            "expires_at": license.expires_at,
            "max_devices": license.max_devices
        })

class LicenseListView(APIView):
    def get(self, request):
        licenses = License.objects.filter(user=request.user)
        return Response(LicenseListSerializer(licenses, many=True).data)


class LicenseDetailView(APIView):
    def get(self, request, pk):
        license = get_object_or_404(
            License,
            key=pk,
            user=request.user
        )

        return Response(LicenseDetailSerializer(license).data)
    

class RevokeMachineView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk, machine_id):
        license = get_object_or_404(
            License,
            key=pk,
            user=request.user
        )
        machine = get_object_or_404(
            MachineActivation,
            license=license,
            machine_id=machine_id
        )

        # déjà révoquée
        if machine.is_revoked:
            return Response({
                "status": "already_revoked"
            })

        machine.is_revoked = True
        machine.save(update_fields=["is_revoked"])

        return Response({
            "status": "revoked"
        })

class ReactivateMachineView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, machine_id):
        license = get_object_or_404(
            License,
            key=pk,
            user=request.user
        )
        machine = get_object_or_404(
            MachineActivation,
            license=license,
            machine_id=machine_id
        )

        if not machine.is_revoked:
            return Response({
                "status": "already_active"
            })

        # vérifier la limite avant réactivation
        active_devices = MachineActivation.objects.filter(
            license=license,
            is_revoked=False
        ).count()

        if active_devices >= license.max_devices:
            return Response(
                {
                    "error": "Device limit reached"
                },
                status=403
            )

        machine.is_revoked = False
        machine.save(
            update_fields=["is_revoked"]
        )

        return Response({
            "status": "reactivated",
            "machine_id": machine.machine_id
        })

class LicenseStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        machine_id = request.GET.get("machine_id")
        user = request.user

        # 🔍 get active license
        license = License.objects.filter(
            user=user,
            active=True
        ).first()

        if not license:
            return Response({
                "valid": False,
                "reason": "no_license"
            })

        # ⛔ expiration
        if not license.is_valid():
            return Response({
                "valid": False,
                "reason": "expired"
            })

        # 🔍 check machine
        activation = MachineActivation.objects.filter(
            license=license,
            machine_id=machine_id
        ).first()

        if not activation:
            return Response({
                "valid": False,
                "reason": "machine_not_activated"
            })

        # 🚫 revoked machine
        if activation.is_revoked:
            return Response({
                "valid": False,
                "reason": "machine_revoked"
            })

        # ✔ valid
        return Response({
            "valid": True,
            "expires_at": license.expires_at,
        })
        

class MachineStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, machine_id):
        license = get_object_or_404(
            License,
            key=pk,
            user=request.user
        )

        if not license.active:
            return Response({
                "valid": False,
                "reason": "license_disabled"
            })

        if not license.is_valid():
            return Response({
                "valid": False,
                "reason": "expired"
            })

        activation = get_object_or_404(
            MachineActivation,
            license=license,
            machine_id=machine_id
        )

        if activation.is_revoked:
            return Response({
                "valid": False,
                "reason": "machine_revoked"
            })


        activation.last_check = timezone.now()
        activation.save(
            update_fields=["last_check"]
        )


        return Response({
            "valid": True,
            "expires_at": license.expires_at,
        })