from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from . import models


class TicketInline(admin.StackedInline):
    model = models.Ticket
    exclude = ["purchased"]
    extra = 1


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "organizer", "category")
    list_filter = ("organizer", "date")
    fields = (
        "title",
        "description",
        "date",
        "location",
        "organizer",
        "category",
    )
    search_fields = ("title", "category__name", "location")
    inlines = [TicketInline]


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "event_count")

    def event_count(self, category):
        url = (
            reverse("admin:events_event_changelist")
            + f"?category__id__exact={category.id}"
        )
        return format_html('<a href="{}">{}</a>', url, category.event_set.count())


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user",)


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "price", "capacity", "purchased", "available")
    list_filter = ("event", "available")
    search_fields = ("event__title", "title")
    autocomplete_fields = ("event",)


@admin.register(models.Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("ticket", "participant", "status", "payment_status")
    list_filter = ("status", "payment_status")
    search_fields = ("participant__username",)
    autocomplete_fields = ("ticket", "participant")
