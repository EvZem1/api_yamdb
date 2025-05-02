from datetime import datetime

from django.core.exceptions import ValidationError

from api.constants import BANNED_USERNAMES


def validate_username(value):
    if value in BANNED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя {value} недопустимо.')


def validate_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(f'Год не может быть больше {current_year}.')
