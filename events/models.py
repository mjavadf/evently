import random
import qrcode
from collections.abc import Iterable
from django.conf import settings
from django.db import models
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files import File

from .validators import validate_image_size


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Location(models.Model):
    # https://github.com/openwisp/django-rest-framework-gis
    # https://github.com/Hipo/drf-extra-fields
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # picture = models.ImageField(upload_to='locations', null=True, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        default=None,
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizing_events",
    )
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.title}"


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="events/images",
        validators=[validate_image_size],
    )


class Ticket(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE, related_name="tickets")
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    capacity = models.IntegerField()
    purchased = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    needs_approval = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} for {self.event}"

    def buy(self):
        if self.available:
            self.purchased += 1
            self.save()
            return True
        else:
            return False

    class Meta:
        unique_together = ("event", "title")


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("P", "Pending"),
        ("A", "Approved"),
        ("R", "Rejected"),
        ("W", "Waitlisted"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("P", "Pending"),
        ("C", "Complete"),
        ("F", "Failed"),
        ("N", "Not Required"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("C", "Credit Card"),
        ("P", "PayPal"),
        ("N", "Not Required"),
    ]

    ticket = models.ForeignKey(
        Ticket, on_delete=models.PROTECT, related_name="reservations"
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reservations"
    )
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="A")
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default="N"
    )
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default="N"
    )
    code = models.PositiveIntegerField(null=True, blank=True, unique=True)
    qrcode = models.ImageField(upload_to='qrcodes',blank=True)
    
    def generate_unique_code(self):
        # Generate a unique 8-digit code
        while True:
            code = random.randint(10000000, 99999999)
            if not Reservation.objects.filter(code=code).exists():
                break
        return code
        

    def save(self,*args, **kwargs):
        # Generate and assign a unique code when saving the reservation
        if not self.code:
            self.code = self.generate_unique_code()
        
        # generate and save qr_code
        if not self.qrcode:
            qrcode_img = qrcode.make(self.code)
            canvas = Image.new("RGB", (300,300),"white")
            draw = ImageDraw.Draw(canvas)
            canvas.paste(qrcode_img)
            buffer = BytesIO()
            canvas.save(buffer,"PNG")
            self.qrcode.save(f'qrcode{self.code}.png',File(buffer),save=False)
            canvas.close()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.participant.username} - {self.ticket.event.title}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    image = models.ImageField(
        upload_to="profiles/images",
        null=True,
        blank=True,
        validators=[validate_image_size],
    )

    def __str__(self):
        return self.user.username
