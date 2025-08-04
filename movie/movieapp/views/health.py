# movieapp/views/health.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from movieapp.utils.tmdb_utils import TMDBUtils
from movieapp.models import Movie

class HealthCheckView(APIView):
    """View for checking the health of the API, database, Redis, and TMDB."""
    def get(self, request):
        """Check the health of the API components.
        
        Returns:
            Response: Health status of database, Redis, and TMDB API.
        """
        try:
            # Check database
            Movie.objects.count()
            # Check Redis
            cache.set('health_check', 'ok', timeout=5)
            redis_ok = cache.get('health_check') == 'ok'
            # Check TMDB API
            tmdb_response = TMDBUtils.get_popular_movies(page=1)
            tmdb_ok = 'results' in tmdb_response
            return Response({
                'status': 'healthy',
                'database': 'ok',
                'redis': 'ok' if redis_ok else 'error',
                'tmdb_api': 'ok' if tmdb_ok else 'error',
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'unhealthy', 'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)