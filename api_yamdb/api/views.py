from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .serializers import SignUpSerializer
from reviews.models import User
from django.shortcuts import get_object_or_404


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            
            # Проверка на уникальность username и email
            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Пользователь с таким email уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': 'Пользователь с таким username уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создание пользователя (confirmation_code генерируется автоматически)
            user = User.objects.create_user(
                username=username,
                email=email,
            )
            
            # Отправка кода на email
            send_mail(
                'Код подтверждения',
                f'Ваш код: {user.confirmation_code}',
                'from@example.com',  # Настройте реальный email в продакшене
                [email],
                fail_silently=False,
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenView(APIView):
    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
        
        if not username or not confirmation_code:
            return Response(
                {'error': 'Оба поля (username и confirmation_code) обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(
                {'error': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Генерация JWT-токена
        from rest_framework_simplejwt.tokens import AccessToken
        access = AccessToken.for_user(user)
        return Response({'token': str(access)}, status=status.HTTP_200_OK)
