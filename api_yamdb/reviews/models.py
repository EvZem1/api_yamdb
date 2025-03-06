import secrets
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import CustomUser as User
from .serializers import *


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, created = User.objects.get_or_create(
            **serializer.validated_data
        )

        confirmation_code = secrets.token_urlsafe(16)
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            'Код подтверждения',
            f'Ваш код: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            username=serializer.validated_data['username'],
            confirmation_code=serializer.validated_data['confirmation_code']
        ).first()

        if not user:
            return Response(
                {'error': 'Неверный код'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    