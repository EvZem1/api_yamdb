from django.contrib import admin

from reviews import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(models.Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'display_genres', 'category',
                    'description')
    list_filter = ('year', 'category')
    search_fields = ('name', 'year', 'description', 'category__name')
    list_editable = ('category',)
    ordering = ('year', 'name')

    @admin.display(description='Жанры')
    def display_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'author', 'score', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    ordering = ('pub_date',)


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    ordering = ('pub_date',)
