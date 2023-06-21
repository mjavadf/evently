from unicodedata import category
from django.db import models
from django.contrib.auth.models import User


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
    capacity = models.IntegerField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizing_events')
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
            self.sold += quantity
            self.available = self.sold < self.capacity
            self.save()
            return True
        return False