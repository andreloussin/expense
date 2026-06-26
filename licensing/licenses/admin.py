from django.contrib import admin
from .models import (
    License,
    MachineActivation
)


class MachineActivationInline(admin.TabularInline):
    model = MachineActivation
    extra = 0


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "active", "expires_at", "max_devices")
    list_filter = ("active",)
    search_fields = ("key", "user__email")
    inlines = [MachineActivationInline]


@admin.register(MachineActivation)
class MachineActivationAdmin(admin.ModelAdmin):
    list_display = ("license", "machine_id", "is_revoked", "last_check", "activated_at")
    list_filter = ("is_revoked",)
    search_fields = ("machine_id",)