from django.core.exceptions import ValidationError

from api_yamdb.constants import UNAVAILABLE_USERNAME


def validate_username_not_me(value):
    if value.lower() == UNAVAILABLE_USERNAME:
        raise ValidationError(
            f'Имя пользователя "{UNAVAILABLE_USERNAME}" '
            'использовать запрещено.'
        )
