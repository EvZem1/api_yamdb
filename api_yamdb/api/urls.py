from django.urls import include, path

from rest_framework.routers import SimpleRouter
from .views import APISignup, APIGetToken, UsersViewSet

router = SimpleRouter()
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
    *router.urls,
]
