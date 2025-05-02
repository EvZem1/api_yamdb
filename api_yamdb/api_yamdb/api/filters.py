from django_filters import rest_framework

from reviews.models import Title


class TitleFilter(rest_framework.FilterSet):
    genre = rest_framework.CharFilter(field_name='genre__slug',
                                      lookup_expr='exact')
    category = rest_framework.CharFilter(field_name='category__slug',
                                         lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['name', 'year', 'genre', 'category']
