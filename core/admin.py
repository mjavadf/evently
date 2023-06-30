from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "phone_number")
    search_fields = ("username",)
    fields = ["username", "email", "phone_number"]
