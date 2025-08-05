# movieapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from movieapp.views.auth_views import token_obtain_pair, token_refresh
from movieapp.views.user_views import UserViewSet, RegisterView
from movieapp.views.movie_views import MovieViewSet
from movieapp.views.favorite_movie_views import FavoriteMovieViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'movies', MovieViewSet)
router.register(r'favorite-movies', FavoriteMovieViewSet, basename='favorite-movie')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', token_obtain_pair, name='token_obtain_pair'),
    path('token/refresh/', token_refresh, name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
]