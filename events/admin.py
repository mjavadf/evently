from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "organizer", "category")
    list_filter = ("organizer", "date")
    fields = (
        "title",
        "slug",
        "description",
        "date",
        "location",
        "capacity",
        "organizer",
        "category",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "category__name", "location")


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "event_count")
    prepopulated_fields = {"slug": ("name",)}

    def event_count(self, category):
        url = (
            reverse("admin:events_event_changelist")
            + f"?category__id__exact={category.id}"
        )
        return format_html('<a href="{}">{}</a>', url, category.event_set.count())
