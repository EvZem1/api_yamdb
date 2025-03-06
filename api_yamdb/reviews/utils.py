
from random import choice
from string import digits

from django.core.mail import send_mail
from django.conf import settings

from .constants import SUBJECT


def generate_confirmation_code():
    return ''.join(choice(digits) for _ in range(6))


def send_confirmation_code(email, confirmation_code):
    subject = SUBJECT
    message = f'Код подтверждения: {confirmation_code}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = (email,)
    send_mail(subject, message, from_email, recipient_list)
