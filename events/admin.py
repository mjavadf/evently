from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from . import models


class TicketInline(admin.StackedInline):
    model = models.Ticket
    exclude = ["purchased"]
    extra = 1
    

# class EventImageInline(admin.StackedInline):
#     model = models.EventImage
#     readonly_fields = ["image_preview"]
    
#     def image_preview(self, obj):
#         if obj.image != "":
#             return format_html(f'<img src="{obj.image.url}" width="200px">')
    

@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "city", "address", "latitude", "longitude")
    search_fields = ("name", "country", "city", "address")
    


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "organizer", "category", "location")
    list_filter = ("organizer", "date")
    fields = (
        "title",
        "description",
        "date",
        "end_date",
        "location",
        "organizer",
        "category",
        "cover",
    )
    search_fields = ("title", "category__name", "location")
    autocomplete_fields = ("location", "organizer", "category")
    inlines = [TicketInline]
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("category", "location")


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "event_count")
    search_fields = ("name",)

    def event_count(self, category):
        url = (
            reverse("admin:events_event_changelist")
            + f"?category__id__exact={category.id}"
        )
        return format_html('<a href="{}">{}</a>', url, category.event_set.count())
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("event_set")


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user",)
    readonly_fields = ["image_preview"]
    
    def image_preview(self, obj):
        if obj.image != "":
            return format_html(f'<img src="{obj.image.url}" width="200px">')


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "price", "capacity", "purchased", "available")
    list_filter = ("event", "available")
    search_fields = ("event__title", "title")
    autocomplete_fields = ("event",)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request)


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("ticket", "participant", "status", "payment_status")
    list_filter = ("status", "payment_status")
    search_fields = ("participant__username",)
    autocomplete_fields = ("ticket", "participant")
    readonly_fields = ["qrcode"]
