from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from reviews.models import Category, Genre, Title, User
from rest_framework import serializers


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'slug']
        model = Genre


class GenreSetSerializer(serializers.SlugRelatedField):
    def to_representation(self, data):
        serializer = GenreSerializer(data)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'slug']
        model = Category


class CategorySetSerializer(serializers.SlugRelatedField):
    def to_representation(self, data):
        serializer = CategorySerializer(data)
        return serializer.data


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySetSerializer(
        slug_field='slug',
        queryset=Category.objects.all(),
        read_only=True,
    )
    genre = GenreSetSerializer(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        read_only=True,
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
        )

    def to_representation(self, instance):
        r = super().to_representation(instance)
        req = self.context.get('request')
        if req and req.method == 'GET':
            r['rating'] = instance.rating
        return r


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя 'me' использовать нельзя")
        return value


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class NotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        fields = '__all__'
        model = Review
