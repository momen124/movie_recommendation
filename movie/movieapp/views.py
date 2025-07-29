from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Movie
from .serializers import MovieSerializer

class MovieViewSet(viewsets.ModelViewSet):
      queryset = Movie.objects.all()
      serializer_class = MovieSerializer
      permission_classes = [IsAuthenticatedOrReadOnly]

      def get_queryset(self):
        cache_key = "movie_list"
        cached_data = cache_instance.get_cache(cache_key)
        if cached_data is not None:
            return cached_data
        tmdb_data = TMDBUtils.get_popular_movies()
        # Process TMDB data and save to DB if needed
        queryset = super().get_queryset()
        cache_instance.set_cache(cache_key, list(queryset), timeout=3600)
        return queryset