from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email_task(subject, message, from_address, to_address, fail_silently=False):
    send_mail(subject, message, from_address, to_address, fail_silently=fail_silently)