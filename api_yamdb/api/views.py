from rest_framework import filters, mixins, viewsets

from reviews.models import Category, Genre, Title
from api.permissions import SafeOrAdminOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import CharFilter, FilterSet


class CategoryViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Category.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    permission_classes = [SafeOrAdminOnly]
    lookup_field = 'slug'
    serializer_class = CategorySerializer


class GenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    search_fields = ['name']
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    permission_classes = [SafeOrAdminOnly]
    serializer_class = GenreSerializer


class TitleFilter(FilterSet):
    category = CharFilter(
        field_name='category__slug',
        lookup_expr='contains',
    )
    genre = CharFilter(
        field_name='genre__slug',
        lookup_expr='contains',
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [SafeOrAdminOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = TitleFilter
    serializer_class = TitleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
