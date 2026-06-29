from django.db.models.signals import post_migrate
from django.dispatch import receiver

from django.db import models
from accounts.models import User
from django.utils import timezone

class PlanType(models.TextChoices):
    FREE = 'FREE', 'Plan Gratuit'
    PRO = 'PRO', 'Plan Professionnel'
    ENTERPRISE = 'ENTERPRISE', 'Plan Entreprise'

class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Actif'
    CANCELED = 'CANCELED', 'Annulé (Finit la période en cours)'
    EXPIRED = 'EXPIRED', 'Expiré'
    PAST_DUE = 'PAST_DUE', 'Impayé'


class PlanConfiguration(models.Model):
    plan_type = models.CharField(
        max_length=20, 
        choices=PlanType.choices, 
        unique=True,
        help_text="Le type de plan concerné par cette configuration"
    )
    max_devices = models.PositiveIntegerField(
        default=1, 
        help_text="Nombre maximum de PC autorisés pour ce plan"
    )
    duration_days = models.PositiveIntegerField(
        default=30, 
        help_text="Durée par défaut de la souscription en jours (ex: 30 pour 1 mois, 365 pour 1 an)"
    )
    price = models.DecimalField(
        max_length=10, 
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )

    def __str__(self):
        return f"Configuration - {self.get_plan_type_display()}"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        default=PlanType.FREE
    )
    status = models.CharField(
        max_length=20, 
        choices=SubscriptionStatus.choices, 
        default=SubscriptionStatus.ACTIVE
    )
    max_devices = models.PositiveIntegerField(default=1)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_type_display()}"

    @property
    def remaining_slots(self):
        active_devices_count = self.user.devices.count()
        return max(0, self.max_devices - active_devices_count)
    
    @property
    def is_valid(self):
        """Vérifie si l'abonnement donne toujours accès au logiciel"""
        return self.status in [SubscriptionStatus.ACTIVE] and timezone.now() <= self.expires_at


@receiver(post_migrate)
def create_default_plans(sender, **kwargs):
    """Génère automatiquement les configurations par défaut si la table est vide"""
    # On s'assure de n'exécuter cela que pour l'application subscriptions
    if sender.name == 'subscriptions':
        if not PlanConfiguration.objects.exists():
            PlanConfiguration.objects.create(plan_type=PlanType.FREE, max_devices=1, duration_days=30, price=0.00)
            PlanConfiguration.objects.create(plan_type=PlanType.PRO, max_devices=3, duration_days=365, price=99.00)
            PlanConfiguration.objects.create(plan_type=PlanType.ENTERPRISE, max_devices=10, duration_days=365, price=499.00)
            print("Configurations de plans par défaut initialisées avec succès !")