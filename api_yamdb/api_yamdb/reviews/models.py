from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import (CHARFIELD_MAX_LENGHT, LIMIT_STRING, MAX_RATING,
                           MIN_RATING)
from api.validators import validate_year
from users.models import User

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    """Кастомная модель пользователя."""
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER,
    )
    email = models.EmailField(
        verbose_name='Email адрес',
        unique=True,
    )


class CategoryGenreBaseModel(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=CHARFIELD_MAX_LENGHT,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        abstract = True

    def __str__(self) -> str:
        return self.name


class ReviewComment(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        max_length=CHARFIELD_MAX_LENGHT,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('pub_date',)
        abstract = True

    def __str__(self) -> str:
        return self.text[:LIMIT_STRING]


class Category(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=256)
    slug = models.SlugField(verbose_name='URL slug', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-id', )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=256)
    slug = models.SlugField(verbose_name='URL slug', unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('-id', )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=256)
    year = models.PositiveSmallIntegerField(
        verbose_name='Год', validators=[validate_year], db_index=True)
    genre = models.ManyToManyField(Genre, through='GenreTitle',
                                   through_fields=('title', 'genre'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 blank=True, null=True, related_name='titles')
    description = models.TextField(verbose_name='Описание', blank=True,
                                   null=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-id', )


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, blank=True,
                              null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, blank=True,
                              null=True)


class Review(ReviewComment):
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(MIN_RATING),
            MaxValueValidator(MAX_RATING)
        ]
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews'
    )

    class Meta:
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review')]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(ReviewComment):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
