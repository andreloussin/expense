from django.db import models
from accounts.models import User

class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=8, help_text="ID unique de 8 caractères généré par Electron")
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Device {self.device_id} ({self.user.username})"
