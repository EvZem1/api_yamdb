from django.db import models

from reviews.validators import validate_year


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

    description = models.TextField(verbose_name='описание', blank=True)
    genre = models.ManyToManyField(Genre, verbose_name='жанр')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='категории',
        null=True,
    )

    year = models.SmallIntegerField(
        db_index=True,
        validators=[validate_year],
        verbose_name='год выхода',
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'
        ordering = ['name']

    def __str__(self):
        return self.name[:30]
