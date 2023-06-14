from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    slug = models.SlugField(max_length=255, unique=True)
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    events = models.ManyToManyField(Event, related_name='categories')
    slug = models.SlugField(max_length=255, unique=True)