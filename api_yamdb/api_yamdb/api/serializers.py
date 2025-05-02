from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api import constants
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=constants.EMAIL_LENGTH)
    username = serializers.CharField(
        required=True,
        max_length=constants.USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=constants.USERNAME_VALIDATOR,
                message=(
                    'Имя пользователя может содержать только буквы, цифры и '
                    'символы @/./+/-/_'),
                code='invalid_username'
            )
        ]
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if username in constants.BANNED_USERNAMES:
            raise serializers.ValidationError(
                f'Использовать имя "{username}" в качестве username запрещено.'
            )
        if email:
            try:
                user = User.objects.get(email=email)
                if user.username != username:
                    raise serializers.ValidationError(
                        'Пользователь с таким email уже существует.'
                    )
            except User.DoesNotExist:
                pass
        if username:
            try:
                user = User.objects.get(username=username)
                if user.email != email:
                    raise serializers.ValidationError(
                        f'Пользователь "{username}" уже существует.'
                    )
            except User.DoesNotExist:
                pass

        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            email=validated_data['email'],
            username=validated_data['username']
        )
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=constants.USERNAME_LENGTH)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound(
                detail={'username':
                        'Пользователь с таким username не найден.'})

        if not user.is_confirmation_code_valid(confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения.'
            )
        attrs['user'] = user
        return attrs

    def get_token(self, user):
        return TokenObtainPairSerializer.get_token(user)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name', 'slug']
        model = Genre


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name', 'slug']
        model = Category


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ['id', 'text', 'author', 'score', 'pub_date']
        model = Review

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(author=user, title_id=title_id).exists():
                raise serializers.ValidationError(
                    "Разрешено оставить только один отзыв к произведению"
                )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ['id', 'text', 'author', 'pub_date']
        model = Comment


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'rating', 'genre', 'category',
            'description']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = CategorySerializer(instance.category).data
        data['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        return data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=constants.USERNAME_LENGTH,
        validators=[
            RegexValidator(
                regex=constants.USERNAME_VALIDATOR,
                message=(
                    'Имя пользователя может содержать только буквы, цифры и '
                    'символы @/./+/-/_'),
                code='invalid_username'
            )
        ]
    )
    email = serializers.EmailField(required=True,
                                   max_length=constants.EMAIL_LENGTH)

    class Meta:
        model = User
        fields = 'username', 'email', 'first_name', 'last_name', 'bio', 'role'

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.')
        if value in constants.BANNED_USERNAMES:
            raise serializers.ValidationError(
                f'Использовать имя {value} в качестве username запрещено.')
        return value

    def validate_role(self, value):
        if self.context['request'].user.is_admin:
            return value
        return constants.USER
