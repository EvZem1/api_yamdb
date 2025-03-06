from rest_framework import serializers

from reviews.models import User


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError("Использовать 'me' нельзя")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 
            'last_name', 'bio', 'role'
        )

    def validate_role(self, value):
        if not self.context['request'].user.is_admin:
            if value != self.instance.role:
                raise serializers.ValidationError("Изменение роли запрещено")
        return value
