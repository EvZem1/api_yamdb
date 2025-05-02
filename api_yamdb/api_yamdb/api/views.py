from http import HTTPStatus
from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, pagination, permissions, response, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend

from api import serializers
from api.filters import TitleFilter
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly, IsAdminOnly
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """
    Базовый ViewSet для создания, получения списка и удаления объектов.
    Используется для категорий и жанров.
    """
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    """ViewSet для работы с категориями."""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    """ViewSet для работы с жанрами."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с произведениями."""
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = serializers.TitleSerializer  # По умолчанию используем TitleWriteSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TitleFilter
    search_fields = ('name', 'description')
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.TitleReadSerializer
        return serializers.TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с отзывами."""
    serializer_class = serializers.ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями."""
    serializer_class = serializers.CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class SignUpView(views.APIView):
    """View для регистрации нового пользователя."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = str(randint(10000, 99999))
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Код подтверждения API Yamdb',
            message=(
                f'Здравствуйте, {user.username}!\n'
                'Если вы получили это письмо по ошибке, проигнорируйте его.\n'
                f'Ваш код подтверждения: {confirmation_code}'
            ),
            from_email=settings.EMAIL_BASE,
            recipient_list=[serializer.validated_data['email']],
            fail_silently=True,
        )
        return Response(serializer.data, status=HTTPStatus.OK)


class TokenObtainView(views.APIView):
    """View для получения JWT токена."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = str(AccessToken.for_user(user))
        return Response({'token': token}, status=HTTPStatus.OK)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly]
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Получение и обновление информации о текущем пользователе."""
        user = request.user
        serializer = self.get_serializer(user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        return Response(serializer.data, status=HTTPStatus.OK)
