# movieapp/utils/tmdb_utils.py
import logging
import requests
from django.conf import settings
from movieapp.constants import TMDB_BASE_URL

logger = logging.getLogger(__name__)

class TMDBUtils:
    """Utility class for interacting with the TMDB API."""
    BASE_URL = TMDB_BASE_URL
    API_KEY = settings.TMDB_API_KEY

    @staticmethod
    def get_popular_movies(page=1):
        """Fetch popular movies from TMDB API for the specified page.
        
        Args:
            page (int): Page number for paginated results (default: 1).
        
        Returns:
            dict: JSON response from TMDB API or {'results': []} on error.
        """
        try:
            url = f"{TMDBUtils.BASE_URL}/movie/popular"
            params = {"api_key": TMDBUtils.API_KEY, "page": page}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"TMDB API error (popular movies, page={page}): {str(e)}")
            return {'results': []}

    @staticmethod
    def get_movie_details(movie_id):
        """Fetch details for a specific movie by TMDB ID.
        
        Args:
            movie_id (int): TMDB movie ID.
        
        Returns:
            dict: Movie details or empty dict on error.
        """
        try:
            url = f"{TMDBUtils.BASE_URL}/movie/{movie_id}"
            params = {"api_key": TMDBUtils.API_KEY}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"TMDB API error (movie details, id={movie_id}): {str(e)}")
            return {}

    @staticmethod
    def get_genre_list():
        """Fetch the list of movie genres from TMDB API.
        
        Returns:
            dict: Mapping of genre IDs to names or empty dict on error.
        """
        try:
            url = f"{TMDBUtils.BASE_URL}/genre/movie/list"
            params = {"api_key": TMDBUtils.API_KEY}
            response = requests.get(url, params=params)
            response.raise_for_status()
            genres = response.json().get('genres', [])
            return {genre['id']: genre['name'] for genre in genres}
        except requests.RequestException as e:
            logger.error(f"TMDB API error (genre list): {str(e)}")
            return {}