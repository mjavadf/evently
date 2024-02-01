from celery import shared_task
from templated_mail.mail import BaseEmailMessage
from django.conf import settings


@shared_task
def send_reservation_mail_task(created, context):
    try:
        if settings.DEBUG:
            context['qrcode'] = 'http://127.0.0.1:8000' + context['qrcode']
        message = BaseEmailMessage(
            template_name="mail/reservation_mail.html",
            context=context,
        )
        message.send(to=[context['reciever']])
        return True
    except Exception as e:
        print(e)
        return False