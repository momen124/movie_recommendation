# movieapp/views/favorite_movie_views.py
import logging
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from movieapp.models import FavoriteMovie
from movieapp.serializers import FavoriteMovieSerializer
from movieapp.utils.cache_utils import CacheMixin
from django.core.cache import cache
from movieapp.constants import PAGE_SIZE  # Updated import

logger = logging.getLogger(__name__)

class FavoriteMovieViewSet(CacheMixin, viewsets.ModelViewSet):
    """ViewSet for managing user favorite movies."""
    serializer_class = FavoriteMovieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get favorite movies for the authenticated user.
        
        Returns:
            QuerySet: Favorite movies ordered by added date.
        """
        return FavoriteMovie.objects.filter(user=self.request.user).order_by('-added_at').prefetch_related('movie__genres')

    def perform_create(self, serializer):
        """Create a new favorite movie for the user and invalidate cache.
        
        Args:
            serializer: FavoriteMovieSerializer instance with validated data.
        """
        instance = serializer.save(user=self.request.user)
        cache_key = self.get_cache_key(self.request, 'favorite_movie_list', self.request.user.id)
        cache.delete(cache_key)
        logger.info(f"Cache invalidated for key: {cache_key} after adding FavoriteMovie id={instance.id}")

    def perform_destroy(self, instance):
        """Delete a favorite movie and invalidate cache.
        
        Args:
            instance: FavoriteMovie instance to delete.
        """
        instance_id = instance.id
        instance.delete()
        cache_key = self.get_cache_key(self.request, 'favorite_movie_list', self.request.user.id)
        cache.delete(cache_key)
        logger.info(f"Cache invalidated for key: {cache_key} after deleting FavoriteMovie id={instance_id}")

    def list(self, request, *args, **kwargs):
        """List favorite movies with pagination and caching.
        
        Args:
            request: HTTP request object.
        
        Returns:
            Response: Paginated list of favorite movies or cached response.
        """
        cache_key = self.get_cache_key(request, 'favorite_movie_list', request.user.id)
        cached_response = self.get_cached_response(cache_key)
        if cached_response:
            return cached_response

        queryset = self.get_queryset()
        logger.info(f"FavoriteMovie queryset count: {queryset.count()}")
        if not queryset.exists():
            empty_response = {'count': 0, 'next': None, 'previous': None, 'results': []}
            self.cache_response(cache_key, empty_response)
            return Response(empty_response)

        self.paginator.page_size = PAGE_SIZE
        try:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                logger.info(f"FavoriteMovie paginated response: count={response.data['count']}, next={response.data['next']}")
                self.cache_response(cache_key, response.data)
                return response
        except Exception as e:
            logger.error(f"FavoriteMovie pagination failed: {str(e)}")

        serializer = self.get_serializer(queryset, many=True)
        self.cache_response(cache_key, serializer.data)
        return Response(serializer.data)