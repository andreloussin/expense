from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    
    @property
    def active_subscription(self):
        """
        Retourne l'abonnement valide actuel de l'utilisateur s'il existe, sinon None.
        Un abonnement est considéré comme actif s'il n'est pas expiré et que son statut
        donne droit à l'accès (ACTIVE).
        """
        # Import local pour éviter les imports circulaires entre les applications
        from subscriptions.models import SubscriptionStatus

        now = timezone.now()
        return self.subscriptions.filter(
            status=SubscriptionStatus.ACTIVE,
            expires_at__gt=now
        ).first()

    @property
    def remaining_slots(self):
        """
        Calcule de manière dynamique les slots de devices restants.
        """
        sub = self.active_subscription
        
        # Si aucun abonnement n'est actif, il reste 0 slot
        if not sub:
            return 0
            
        active_devices_count = self.devices.count()
        return max(0, sub.max_devices - active_devices_count)
