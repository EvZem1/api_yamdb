from reviews.models import Category, Genre, Title
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
    )
    genre = GenreSetSerializer(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )

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
