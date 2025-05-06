from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api_yamdb import constants

from .validators import validate_username_not_me


class UserRole(models.TextChoices):
    USER = 'user', 'User'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        'username',
        max_length=constants.LIMIT_USERNAME,
        unique=True,
        help_text=(
            f'Обязательное поле. Не более {constants.LIMIT_USERNAME} символов. '
            'Только буквы, цифры и @/./+/-/_.'
        ),
        validators=[username_validator, validate_username_not_me],
        error_messages={
            'unique': "Пользователь с таким именем уже существует.",
        },
    )
    email = models.EmailField(
        max_length=constants.LIMIT_EMAIL,
        unique=True,
        null=False,
        verbose_name='Адрес электронной почты'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    role = models.CharField(
        max_length=constants.LIMIT_ROLE_LENGTH,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR
