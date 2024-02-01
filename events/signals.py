from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_reservation_mail_task
from .models import Profile, Reservation


# create a profile for every user that is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# send email after making reservation
@receiver(post_save, sender=Reservation)
def send_email(sender, instance, created, **kwargs):
    context = {'created': created, 
                'username': instance.participant.username,
                'status': instance.status,
                'code': instance.code,
                'event_title': instance.ticket.event.title,
                'event_date': instance.ticket.event.date,
                'event_location': instance.ticket.event.location,
                'reciever': instance.participant.email,
                "qrcode": instance.qrcode.url if instance.qrcode else "",}
    send_reservation_mail_task.delay(created, context)
