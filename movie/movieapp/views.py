# movieapp/views.py
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Movie, Genre, FavoriteMovie
from .serializers import UserSerializer, MovieSerializer, FavoriteMovieSerializer
from .utils.utils import TMDBUtils
import logging

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = UserSerializer(user).data
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        cache_key = f"movie_list_page_{request.GET.get('page', '1')}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Returning cached data for page {request.GET.get('page', '1')}")
            return Response(cached_data)

        page = int(request.GET.get('page', '1'))
        tmdb_data = TMDBUtils.get_popular_movies(page=page)
        if not tmdb_data.get('results'):
            logger.warning("No results from TMDB API")
            return Response({'count': 0, 'next': None, 'previous': None, 'results': []})

        genre_map = TMDBUtils.get_genre_list()
        for movie_data in tmdb_data.get('results', []):
            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_data.get('id'),
                defaults={
                    'title': movie_data.get('title'),
                    'description': movie_data.get('overview') or '',
                    'release_date': movie_data.get('release_date') or None,
                    'poster_path': f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get('poster_path') else None,
                }
            )
            genre_ids = movie_data.get('genre_ids', [])
            if genre_ids:
                genres = []
                for genre_id in genre_ids:
                    genre_name = genre_map.get(genre_id, f"Genre {genre_id}")
                    genre, _ = Genre.objects.get_or_create(id=genre_id, defaults={'name': genre_name})
                    genres.append(genre)
                movie.genres.set(genres)

        queryset = self.get_queryset()
        logger.info(f"Queryset count: {queryset.count()}")
        if not queryset.exists():
            logger.warning("Queryset is empty after TMDB sync")
            return Response({'count': 0, 'next': None, 'previous': None, 'results': []})

        self.paginator.page_size = 20
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            logger.info(f"Paginated response: count={response.data['count']}, next={response.data['next']}")
            cache.set(cache_key, response.data, timeout=60 * 15)
            return response

        logger.error("Pagination failed unexpectedly")
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60 * 15)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 15))
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

class FavoriteMovieViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteMovieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user).order_by('-added_at')

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        # Invalidate cache for this user's favorite movies list
        cache_key = f"favorite_movie_list_{self.request.user.id}_page_1"
        cache.delete(cache_key)
        logger.info(f"Cache invalidated for key: {cache_key} after adding FavoriteMovie id={instance.id}")

    def perform_destroy(self, instance):
        instance_id = instance.id
        instance.delete()
        # Invalidate cache for this user's favorite movies list
        cache_key = f"favorite_movie_list_{self.request.user.id}_page_1"
        cache.delete(cache_key)
        logger.info(f"Cache invalidated for key: {cache_key} after deleting FavoriteMovie id={instance_id}")

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        cache_key = f"favorite_movie_list_{request.user.id}_page_{request.GET.get('page', '1')}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Returning cached favorite movies for user {request.user.id}, page {request.GET.get('page', '1')}")
            return Response(cached_data)

        queryset = self.get_queryset()
        logger.info(f"FavoriteMovie queryset count: {queryset.count()}")
        if not queryset.exists():
            cache.set(cache_key, {'count': 0, 'next': None, 'previous': None, 'results': []}, timeout=60 * 15)
            return Response({'count': 0, 'next': None, 'previous': None, 'results': []})

        self.paginator.page_size = 20
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            logger.info(f"FavoriteMovie paginated response: count={response.data['count']}, next={response.data['next']}")
            cache.set(cache_key, response.data, timeout=60 * 15)
            return response

        logger.error("FavoriteMovie pagination failed unexpectedly")
        serializer = self.get_serializer(queryset, many=True)
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

token_obtain_pair = CustomTokenObtainPairView.as_view()
token_refresh = TokenRefreshView.as_view()