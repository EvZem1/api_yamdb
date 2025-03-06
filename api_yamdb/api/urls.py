from django.urls import path

from .views import SignUpView, TokenView

app_name = 'api'

urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenView.as_view(), name='token'),
]
