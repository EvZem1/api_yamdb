from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import mixins, pagination, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User
from users.permissions import (IsAdmin, IsAdminOrReadOnly,
                               IsAuthorModeratorAdminOrReadOnly)

from .filters import TitleFilter
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleGETSerializer, TitleSerializer, TokenSerializer,
                          UserSerializer)


class CDLViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                 mixins.ListModelMixin, GenericViewSet):
    pass


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CDLViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class GenreViewSet(CDLViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)


class TitleViewSet(ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с отзывами (Reviews)."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)

    def get_queryset(self):
        return Review.objects.filter(title_id=self.kwargs['title_id'])

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями к отзывам."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)


class TokenObtainView(APIView):
    """Получение JWT токена по username и confirmation_code."""
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_instance = serializer.validated_data['user']
        token = AccessToken.for_user(user_instance)
        return Response(
            {'token': str(token)},
            status=status.HTTP_200_OK
        )


class SignUpView(APIView):
    """Регистрация нового пользователя или получение confirmation_code."""
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями (только для админов)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = pagination.LimitOffsetPagination # Добавил пагинацию для пользователей

    def get_queryset(self):
        """Добавляем возможность поиска по username."""
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(username__icontains=search_term)
        return queryset

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,),
        url_path='me',
        url_name='users_me'
    )
    def me(self, request, *args, **kwargs):
        """Получение и обновление данных своего профиля."""
        current_user = request.user
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                current_user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=current_user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(current_user)
        return Response(serializer.data, status=status.HTTP_200_OK)
