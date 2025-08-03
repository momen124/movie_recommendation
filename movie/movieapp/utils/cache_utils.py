# movieapp/utils/cache_utils.py
import logging
from django.core.cache import cache
from rest_framework.response import Response
from movieapp.constants import CACHE_TIMEOUT, PAGE_SIZE

logger = logging.getLogger(__name__)

class CacheMixin:
    """Mixin for handling caching in ViewSets."""
    cache_timeout = CACHE_TIMEOUT
    page_size = PAGE_SIZE

    def get_cache_key(self, request, prefix, identifier=''):
        """Generate a cache key based on request and identifier.
        
        Args:
            request: HTTP request object.
            prefix (str): Cache key prefix (e.g., 'movie_list').
            identifier (str): Optional identifier (e.g., user ID).
        
        Returns:
            str: Cache key string.
        """
        page = request.GET.get('page', '1')
        return f"{prefix}_{identifier}_page_{page}"

    def get_cached_response(self, cache_key):
        """Retrieve cached data for the given cache key.
        
        Args:
            cache_key (str): Cache key to retrieve.
        
        Returns:
            Response: Cached response or None if not found.
        """
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Returning cached data for {cache_key}")
            return Response(cached_data)
        return None

    def cache_response(self, cache_key, data):
        """Cache response data with the given cache key.
        
        Args:
            cache_key (str): Cache key to store data.
            data: Data to cache (e.g., serialized response).
        """
        cache.set(cache_key, data, timeout=self.cache_timeout)
        logger.info(f"Cached data for {cache_key}")