from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from api import constants
from api.validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=constants.USERNAME_LENGTH,
        unique=True,
        validators=[
            validate_username,
            RegexValidator(
                regex=constants.USERNAME_VALIDATOR,
                message=(
                    'Имя пользователя может содержать только буквы, цифры и '
                    'символы @/./+/-/_')),
        ]
    )
    role = models.CharField(
        'Роль',
        max_length=constants.ROLE_NAME_LENGTH,
        choices=constants.ROLE_CHOICES,
        default=constants.USER,
    )
    bio = models.TextField('Биография', blank=True)
    confirmation_code_hash = models.CharField(
        'Код подтверждения',
        max_length=constants.CONFIRMATION_CODE_LENGTH,
        blank=True,
        null=True)
    confirmation_code_created_at = models.TextField(
        'Время создания кода подтверждения',
        blank=True,
        null=True)

    def __str__(self):
        return self.username[:constants.USERNAME_LENGTH]

    @property
    def is_admin(self):
        return self.role == constants.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == constants.MODERATOR

    def set_confirmation_code(self, code):
        """Устанавливает хешированный код подтверждения и время создания."""
        self.confirmation_code_hash = make_password(code)
        self.confirmation_code_created_at = timezone.now().strftime(
            '%d-%m-%dY %H:%M:%S'
        )
        self.save()

    def is_confirmation_code_valid(self, code):
        """Проверяет, совпадает ли код."""
        return check_password(code, self.confirmation_code_hash)
