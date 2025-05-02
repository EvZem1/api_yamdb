import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов в базу данных'

    def add_arguments(self, parser):
        files = [
            'categories', 'genres', 'titles', 'users',
            'reviews', 'comments', 'genre_title'
        ]
        for file in files:
            parser.add_argument(
                f'--{file}',
                type=str,
                help=f'Путь к CSV-файлу с {file}'
            )

    def handle_category(self, row):
        Category.objects.get_or_create(**row)

    def handle_genre(self, row):
        Genre.objects.get_or_create(**row)

    def handle_title(self, row):
        category = Category.objects.get(id=row.pop('category'))
        Title.objects.get_or_create(category=category, **row)

    def handle_user(self, row):
        User.objects.get_or_create(**row)

    def handle_review(self, row):
        title = Title.objects.get(id=row.pop('title_id'))
        author = User.objects.get(id=row.pop('author'))
        Review.objects.get_or_create(title=title, author=author, **row)

    def handle_comment(self, row):
        review = Review.objects.get(id=row.pop('review_id'))
        author = User.objects.get(id=row.pop('author'))
        Comment.objects.get_or_create(review=review, author=author, **row)

    def handle_genre_title(self, row):
        title = Title.objects.get(id=row['title_id'])
        genre = Genre.objects.get(id=row['genre_id'])
        title.genre.add(genre)

    @transaction.atomic
    def handle(self, *args, **options):
        handlers = {
            'categories': (self.handle_category, ['id', 'name', 'slug']),
            'genres': (self.handle_genre, ['id', 'name', 'slug']),
            'titles': (self.handle_title, ['id', 'name', 'year', 'category',
                                           'description']),
            'users': (self.handle_user, ['id', 'username', 'email', 'role',
                                         'bio', 'first_name', 'last_name']),
            'reviews': (self.handle_review, ['id', 'title_id', 'text',
                                             'author', 'score', 'pub_date']),
            'comments': (self.handle_comment, ['id', 'review_id', 'text',
                                               'author', 'pub_date']),
            'genre_title': (self.handle_genre_title, ['id', 'title_id',
                                                      'genre_id']),
        }

        for model, (handler, fields) in handlers.items():
            if file_path := options.get(model):
                self.process_file(model, file_path, handler, fields)

    def process_file(self, model_name, file_path, handler, expected_fields):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        filtered_row = {
                            field: row[field] for field in expected_fields}
                        handler(filtered_row)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f'Ошибка в строке {reader.line_num}: {e}'
                        ))
                self.stdout.write(self.style.SUCCESS(
                    f'Данные для {model_name} успешно импортированы!'
                ))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при обработке {model_name}: {e}'
            ))
