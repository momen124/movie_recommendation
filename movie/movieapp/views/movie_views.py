# movieapp/views/movie_views.py
from ratelimit.decorators import ratelimit
from movieapp.utils.tmdb_utils import TMDBUtils
from movieapp.utils.sync_utils import sync_tmdb_movies

class MovieViewSet(CacheMixin, viewsets.ModelViewSet):
    """ViewSet for managing movie data with TMDB integration."""
    queryset = Movie.objects.all().order_by('id').prefetch_related('genres')
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @ratelimit(key='ip', rate='100/h', method='GET')
    def list(self, request, *args, **kwargs):
        """List movies with pagination and TMDB syncing.
        
        Args:
            request: HTTP request object.
        
        Returns:
            Response: Paginated list of movies or cached response.
        """
        cache_key = self.get_cache_key(request, 'movie_list')
        cached_response = self.get_cached_response(cache_key)
        if cached_response:
            return cached_response

        page = int(request.GET.get('page', '1'))
        sync_tmdb_movies(page=page)

        queryset = self.get_queryset()
        logger.info(f"Queryset count: {queryset.count()}")
        if not queryset.exists():
            logger.warning("Queryset is empty after TMDB sync")
            empty_response = {'count': 0, 'next': None, 'previous': None, 'results': []}
            self.cache_response(cache_key, empty_response)
            return Response(empty_response)

        self.paginator.page_size = 20
        try:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                logger.info(f"Paginated response: count={response.data['count']}, next={response.data['next']}")
                self.cache_response(cache_key, response.data)
                return response
        except Exception as e:
            logger.error(f"Pagination failed: {str(e)}")

        serializer = self.get_serializer(queryset, many=True)
        self.cache_response(cache_key, serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single movie by ID with TMDB details.
        
        Args:
            request: HTTP request object.
            kwargs: URL parameters including movie ID.
        
        Returns:
            Response: Movie details or cached response.
        """
        cache_key = self.get_cache_key(request, 'movie_detail', kwargs.get('pk'))
        cached_response = self.get_cached_response(cache_key)
        if cached_response:
            return cached_response

        instance = self.get_object()
        tmdb_data = TMDBUtils.get_movie_details(instance.tmdb_id)
        serializer = self.get_serializer(instance)
        self.cache_response(cache_key, serializer.data)
        return Response(serializer.data)