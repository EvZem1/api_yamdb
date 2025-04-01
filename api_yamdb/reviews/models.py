
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.crypto import get_random_string

from reviews.validators import validate_username, validate_year

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'
ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class User(AbstractUser):
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    bio = models.TextField(
        'биография',
        blank=True,
    )
    confirmation_code = models.CharField(
        'код подтверждения',
        max_length=255,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def generate_confirmation_code(self):
        return get_random_string(length=32)


@receiver(post_save, sender=User)
def post_save(sender, instance, created, **kwargs):
    if created:
        instance.confirmation_code = instance.generate_confirmation_code()
        instance.save()


class Category(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=256,
    )

    slug = models.SlugField(
        verbose_name='идентификатор',
        max_length=50,
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']
        # abstract = True

    def __str__(self):
        return self.name[:30]


class Genre(models.Model):
    slug = models.SlugField(
        verbose_name='идентификатор',
        unique=True,
        db_index=True,
        max_length=50,
    )

    name = models.CharField(
        verbose_name='название',
        max_length=256,
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'
        # abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name[:30]


class Title(models.Model):
    name = models.CharField(
        verbose_name='название',
        db_index=True,
        max_length=256,
    )
    description = models.TextField(
        'описание',
        max_length=255,
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',

        verbose_name='категория',
        null=True,
        blank=True
    )

    year = models.SmallIntegerField(
        db_index=True,
        validators=[validate_year],
        verbose_name='год выхода',
    )

    rating = models.IntegerField(
        'рейтинг',
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'
        ordering = ['name']

    def __str__(self):
        return self.name[:30]


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    text = models.CharField(
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор'
    )
    score = models.IntegerField(
        'оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка от 1 до 10!'}
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review'
            )]
        ordering = ('pub_date',)

    def __str__(self):
        return self.title[:30]


@receiver([post_save, post_delete], sender=Review)
def update_title_rating(sender, instance, **kwargs):
    title = instance.title
    avg_rating = title.reviews.aggregate(models.Avg('score'))['score__avg']
    title.rating = round(avg_rating) if avg_rating else None
    title.save()
