import logging
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from ..models import Movie
from ..serializers import MovieSerializer
from ..utils import sync_tmdb_movies
from .mixins import CacheMixin

logger = logging.getLogger(__name__)

class MovieViewSet(CacheMixin, viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by('id').prefetch_related('genres')  # Optimize genre fetching
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request, 'movie_list')
        cached_response = self.get_cached_response(cache_key)
        if cached_response:
            return cached_response

        # Sync TMDB data
        page = int(request.GET.get('page', '1'))
        sync_tmdb_movies(page=page)

        # Fetch queryset
        queryset = self.get_queryset()
        logger.info(f"Queryset count: {queryset.count()}")
        if not queryset.exists():
            logger.warning("Queryset is empty after TMDB sync")
            empty_response = {'count': 0, 'next': None, 'previous': None, 'results': []}
            self.cache_response(cache_key, empty_response)
            return Response(empty_response)

        # Paginate and serialize
        self.paginator.page_size = 20
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            logger.info(f"Paginated response: count={response.data['count']}, next={response.data['next']}")
            self.cache_response(cache_key, response.data)
            return response

        logger.error("Pagination failed unexpectedly")
        serializer = self.get_serializer(queryset, many=True)
        self.cache_response(cache_key, serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request, 'movie_detail', kwargs.get('pk'))
        cached_response = self.get_cached_response(cache_key)
        if cached_response:
            return cached_response

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.cache_response(cache_key, serializer.data)
        return Response(serializer.data)