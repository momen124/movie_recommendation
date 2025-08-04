import logging
from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class CacheMixin:
    """Mixin for handling caching in ViewSets."""
    cache_timeout = 60 * 15  # 15 minutes

    def get_cache_key(self, request, prefix, identifier=''):
        """Generate a cache key based on request and identifier."""
        page = request.GET.get('page', '1')
        return f"{prefix}_{identifier}_page_{page}"

    def get_cached_response(self, cache_key):
        """Retrieve cached data."""
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Returning cached data for {cache_key}")
            return Response(cached_data)
        return None

    def cache_response(self, cache_key, data):
        """Cache response data."""
        cache.set(cache_key, data, timeout=self.cache_timeout)
        logger.info(f"Cached data for {cache_key}")