from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Profile, Reservation


# create a profile for every user that is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# send email after making reservation
@receiver(post_save, sender=Reservation)
def send_email(sender, instance, created, **kwargs):
    if created:
        subject = "Reservation Confirmation"
        match instance.status:
            case "P":
                message = f"""Dear {instance.participant.username},\n\nThank you for your reservation.\n\nYour reservation is pending approval.\nWe will notify you when it is approved.\n\nBest regards,\n\nThe Evently Team"""
            case "R":
                message = f"""Dear {instance.participant.username},\n\nThank you for your reservation.\n\nYour reservation has been rejected.\nPlease contact us for more information.\n\nBest regards,\n\nThe Evently Team"""
            case "W":
                message = f"""Dear {instance.participant.username},\n\nThank you for your reservation.\n\nYour reservation has been waitlisted.\nWe will notify you when it is approved.\n\nBest regards,\n\nThe Evently Team"""
            case _:
                message = f"""Dear {instance.participant.username},\n\nThank you for your reservation.\n\nYour reservation has been approved.\n\nBest regards,\n\nThe Evently Team"""
                
        to = instance.participant.email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [to], fail_silently=False)
    
    else:
        subject = "Reservation Confirmation"
        match instance.status:
            case "P":
                message = f"""Dear {instance.participant.username},\n\nYour reservation is pending approval.\nWe will notify you when it is approved.\n\nBest regards,\n\nThe Evently Team"""
            case "R":
                message = f"""Dear {instance.participant.username},\n\nYour reservation has been rejected.\nPlease contact us for more information.\n\nBest regards,\n\nThe Evently Team"""
            case "W":
                message = f"""Dear {instance.participant.username},\n\nYour reservation has been waitlisted.\nWe will notify you when it is approved.\n\nBest regards,\n\nThe Evently Team"""
            case _:
                message = f"""Dear {instance.participant.username},\n\nYour reservation has been approved.\n\nBest regards,\n\nThe Evently Team"""
        to = instance.participant.email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [to], fail_silently=False)
