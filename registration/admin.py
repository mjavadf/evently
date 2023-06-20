from django.contrib import admin
from . import models


@admin.register(models.Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "participant", "status")
    list_filter = ["status", 'payment_status']
    search_fields = ("event__title", "user__username")
    fields = [
        "participant",
        "event",
        "status",
        "payment_status",
        "payment_amount",
        "payment_method",
    ]
    autocomplete_fields = ["participant", "event"]
