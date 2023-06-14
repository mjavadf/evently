from django.db import models
from events.models import Event
from django.contrib.auth.models import User

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
    participant = models.ForeignKey(User, on_delete=models.PROTECT)
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
