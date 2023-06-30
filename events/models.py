from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizing_events')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    
    def __str__(self):
        return f'{self.title} by {self.organizer}'


class Ticket(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    capacity = models.IntegerField()
    purchased = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.title} for {self.event}'
    
    def buy(self, quantity=1):
        if self.available:
            self.purchased += quantity
            self.available = self.purchased < self.capacity
            self.save()
            return True
        return False
    
    
class Registration(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('W', 'Waitlisted'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Complete'),
        ('F', 'Failed'),
        ('N', 'Not Required')
    ]
    
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, 
                              choices=STATUS_CHOICES, 
                              default='P')
    payment_status = models.CharField(max_length=1,
                                      choices=PAYMENT_STATUS_CHOICES, 
                                      default='N')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, default='Not Required')
    
    def __str__(self):
        return f"{self.participant.username} - {self.event.title} Registration"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username