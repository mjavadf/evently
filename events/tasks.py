from celery import shared_task
from templated_mail.mail import BaseEmailMessage


@shared_task
def send_reservation_mail_task(created, context):
    try:
        
        message = BaseEmailMessage(
            template_name="mail/reservation_mail.html",
            context=context,
        )
        message.send(to=[context['reciever']])
        return True
    except Exception as e:
        print(e)
        return False