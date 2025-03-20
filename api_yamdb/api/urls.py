from django.urls import include, path
from api.views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
