from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.constants import LIMIT_EMAIL


class UserRole(models.TextChoices):
    USER = 'user', 'User'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'


class User(AbstractUser):
    email = models.EmailField(
        max_length=LIMIT_EMAIL,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Адрес электронной почты'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Код подтверждения',
        editable=False
    )

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    def __str__(self):
        return self.username
