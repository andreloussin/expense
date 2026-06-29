from django.contrib import admin
from .models import PlanConfiguration, Subscription

@admin.register(PlanConfiguration)
class PlanConfigurationAdmin(admin.ModelAdmin):
    # Les colonnes qui s'afficheront dans la liste des configurations
    list_display = ('plan_type', 'max_devices', 'duration_days', 'price')
    
    # Permet de cliquer et modifier directement ces valeurs depuis la liste
    list_editable = ('max_devices', 'duration_days', 'price')
    
    # Empêche de créer deux fois le même type de plan par erreur
    radio_fields = {"plan_type": admin.HORIZONTAL}

# @admin.register(Subscription)
# class SubscriptionAdmin(admin.ModelAdmin):
#     list_display = ('user', 'plan_type', 'status', 'starts_at', 'expires_at', 'is_currently_valid')
#     list_filter = ('plan_type', 'status')
#     search_fields = ('user__email', 'user__name')
