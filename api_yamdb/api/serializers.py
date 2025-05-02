from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api import constants
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name')


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=MAX_LENGTH_150,
        required=True,
        validators=[validate_username],
    )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        errors = {}

        user = User.objects.filter(
            Q(username=username) | Q(email=email)
        ).first()
        if user:
            if user.username != username and user.email == email:
                errors["email"] = [
                    "Этот email уже используется с другим username."
                ]
            if user.email != email and user.username == username:
                errors["username"] = [
                    "Этот username уже используется с другим email."
                ]

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']

        user, _ = User.objects.get_or_create(username=username,
                                             email=email)

        confirmation_code = default_token_generator.make_token(user)

        try:
            send_mail(
                subject="Код подтверждения для YaMDB",
                message=f"Ваш код подтверждения: {confirmation_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except Exception as e:
            raise serializers.ValidationError(
                f"Ошибка при отправке email: {str(e)}. Попробуйте позже."
            )

        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(
        max_length=MAX_LENGTH_150,
        required=True,
        help_text="Укажите username."
    )
    confirmation_code = serializers.CharField(
        required=True,
        help_text="Код подтверждения, отправленный на email."
    )

    def validate(self, data):
        """
        Проверяем код подтверждения для указанного пользователя.
        """
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = User.objects.filter(username=username).first()

        if not user:
            raise NotFound({'detail':
                            'Пользователь с таким username не найден.'})

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError({'detail':
                                               'Неверный код подтверждения.'})

        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug', many=True,
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST' and Review.objects.filter(
            author=request.user, title__id=self.context['view'].get_title().id
        ).exists():
            raise ValidationError('Вы уже оставили отзыв на это произведение.')
        return data
