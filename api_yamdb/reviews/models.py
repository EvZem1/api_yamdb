from api.validators import validate_score_range
from django.db import models
from titles.models import Title
from users.models import User

from api_yamdb.constants import MAX_TEXT_LENGTH


class AbstractReviewComment(models.Model):
    """Абстрактная базовая модель для отзывов и комментариев"""

    text = models.TextField(
        verbose_name='Текст',
        help_text='Основной текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        editable=False,
        related_name='%(class)ss'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return (
            self.text[:MAX_TEXT_LENGTH] + '...'
            if len(self.text) > MAX_TEXT_LENGTH
            else self.text
        )


class Review(AbstractReviewComment):
    """Модель для хранения отзывов на произведения."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Объект отзыва'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[validate_score_range]
    )

    class Meta(AbstractReviewComment.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review_per_author'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв {self.id} от {self.author.username}'


class Comment(AbstractReviewComment):
    """Модель для комментариев к отзывам."""

    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE
    )

    class Meta(AbstractReviewComment.Meta):  # Тут наследую Meta от base class
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
