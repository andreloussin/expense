from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .models import Subscription, PlanConfiguration, PlanType, SubscriptionStatus
from .serializers import PlanConfigurationSerializer, SubscriptionSerializer, SubscribeRequestSerializer

class PlanListView(APIView):
    permission_classes = [AllowAny] # Tout le monde peut voir les plans disponibles

    def get(self, request):
        """1. LIST PLANS : Récupérer toutes les offres configurées en BDD"""
        configs = PlanConfiguration.objects.all()
        serializer = PlanConfigurationSerializer(configs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Récupérer l'abonnement actif (renvoie un objet ou None)
        subscription = request.user.active_subscription

        # Si l'utilisateur n'a aucun abonnement actif ou valide
        if subscription is None:
            return Response({
                "message": "Aucun abonnement actif trouvé pour cet utilisateur."
            }, status=status.HTTP_404_NOT_FOUND)

        # Si un abonnement existe, on le sérialise proprement
        serializer = SubscriptionSerializer(subscription)
        
        return Response(serializer.data, status=status.HTTP_200_OK)




class ProcessSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = SubscribeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        chosen_plan = serializer.validated_data['plan_type']

        # 1. Charger la config du plan demandé
        config = PlanConfiguration.objects.filter(plan_type=chosen_plan).first()
        if not config:
            return Response({"error": "Configuration du plan introuvable."}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        
        # 2. Trouver l'abonnement en cours de validité (s'il existe)
        # On cherche les abonnements non expirés et qui ont un accès (ACTIVE ou CANCELED)
        current_sub = request.user.active_subscription

        # --- CAS 1 : AUCUN ABONNEMENT EN COURS (Nouveau ou Expiré) ---
        if not current_sub:
            new_sub = Subscription.objects.create(
                user=request.user,
                plan_type=chosen_plan,
                status=SubscriptionStatus.ACTIVE,
                max_devices=config.max_devices,
                starts_at=now,
                expires_at=now + timedelta(days=config.duration_days)
            )
            return Response({
                "message": "Souscription activée.",
                "subscription": SubscriptionSerializer(new_sub).data
            }, status=status.HTTP_201_CREATED)

        # --- CAS 2 : PROLONGATION DU MÊME PLAN ---
        if current_sub.plan_type == chosen_plan:            
            # On accumule le temps (stacking) à la suite de l'ancienne date
            current_sub.expires_at = current_sub.expires_at + timedelta(days=config.duration_days)
            current_sub.save()

            return Response({
                "message": f"Votre abonnement {current_sub.get_plan_type_display()} a été prolongé.",
                "subscription": SubscriptionSerializer(current_sub).data
            }, status=status.HTTP_200_OK)

        # --- CAS 3 : CHANGEMENT DE PLAN (UPGRADE OU DOWNGRADE) ---
        # Déterminer si c'est un Upgrade ou Downgrade en comparant les quotas de devices ou prix
        # Ici on compare les quotas de devices pour l'exemple
        is_upgrade = config.max_devices > current_sub.max_devices

        if is_upgrade:
            # UX d'Upgrade : Immédiat. On passe l'ancien en "EXPIRED" prématurément
            current_sub.status = SubscriptionStatus.EXPIRED
            current_sub.save()

            # On crée le nouveau plan qui démarre aujourd'hui
            new_sub = Subscription.objects.create(
                user=request.user,
                plan_type=chosen_plan,
                status=SubscriptionStatus.ACTIVE,
                max_devices=config.max_devices,
                starts_at=now,
                expires_at=now + timedelta(days=config.duration_days)
            )
            return Response({
                "message": f"Surclassement immédiat vers le plan {new_sub.get_plan_type_display()} réussi !",
                "subscription": SubscriptionSerializer(new_sub).data
            }, status=status.HTTP_200_OK)

        else:
            # UX de Downgrade : On ne casse pas son plan actuel plus cher.
            # On planifie le changement. Dans un vrai SaaS, on stockerait un `pending_plan`.
            # Pour rester simple et offrir une bonne UX : on refuse le downgrade immédiat si l'actuel est trop haut,
            # et on invite à attendre la fin ou à annuler.
            return Response({
                "error": f"Vous êtes actuellement sur le plan {current_sub.get_plan_type_display()} "
                         f"qui est supérieur. Vous pourrez choisir le plan {config.get_plan_type_display()} "
                         f"lorsque votre abonnement actuel expirera le {current_sub.expires_at.strftime('%d/%m/%Y')}."
            }, status=status.HTTP_400_BAD_REQUEST)
            
class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Permet à l'utilisateur d'annuler le renouvellement de son abonnement actuel."""
        now = timezone.now()
        current_sub = Subscription.objects.filter(
            user=request.user,
            status=SubscriptionStatus.ACTIVE,
            expires_at__gt=now
        ).first()

        if not current_sub:
            return Response({"error": "Aucun abonnement actif modifiable trouvé."}, status=status.HTTP_404_NOT_FOUND)

        current_sub.status = SubscriptionStatus.CANCELED
        current_sub.save()

        return Response({
            "message": "Votre abonnement a été annulé. Vous continuerez à bénéficier de vos accès jusqu'au "
                       f"{current_sub.expires_at.strftime('%d/%m/%Y')}.",
            "subscription": SubscriptionSerializer(current_sub).data
        }, status=status.HTTP_200_OK)