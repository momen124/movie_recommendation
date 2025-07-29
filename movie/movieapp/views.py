from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, Movie
from .serializers import UserSerializer, MovieSerializer
from .utils.utils import TMDBUtils

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [permissions.IsAdminUser()]

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by('id')
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @cache_page(60 * 15)
    def list(self, request, *args, **kwargs):
        cache_key = f"movie_list_page_{request.GET.get('page', '1')}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return self.get_paginated_response(cached_data)

        page = int(request.GET.get('page', 1))
        tmdb_data = TMDBUtils.get_popular_movies(page=page)
        for movie_data in tmdb_data.get('results', []):
            Movie.objects.update_or_create(
                tmdb_id=movie_data.get('id'),
                defaults={
                    'title': movie_data.get('title'),
                    'description': movie_data.get('overview'),
                    'release_date': movie_data.get('release_date'),
                    'poster_path': movie_data.get('poster_path'),
                }
            )

        queryset = super().get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60 * 15)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        cache_key = f"movie_detail_{kwargs.get('pk')}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        instance = self.get_object()
        tmdb_data = TMDBUtils.get_movie_details(instance.tmdb_id)
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, timeout=60 * 15)
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        user.save()

token_obtain_pair = TokenObtainPairView.as_view()
token_refresh = TokenRefreshView.as_view()