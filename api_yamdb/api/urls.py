from django.urls import include, path

from api.views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    APISignup,
    APIGetToken,
    UsersViewSet,
)
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()

router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register('titles', TitleViewSet)


urlpatterns = [
    path('v1/auth/signup/', APISignup.as_view(), name='signup'),
    path('v1/auth/token/', APIGetToken.as_view(), name='get_token'),
    path('v1', include(router_v1.urls)),
]
