from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet
from .views import MovieViewSet, token_obtain_pair, token_refresh

router = DefaultRouter()
router.register(r'movies', MovieViewSet)

urlpatterns = [
      path('', include(router.urls)),
       path('token/', token_obtain_pair, name='token_obtain_pair'),
      path('token/refresh/', token_refresh, name='token_refresh'),
  ]