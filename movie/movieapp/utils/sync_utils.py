import logging
from django.core.cache import cache
from movieapp.models import Movie, Genre
from movieapp.utils.tmdb_utils import TMDBUtils

logger = logging.getLogger(__name__)

def sync_tmdb_movies(page=1):
    """Sync popular movies from TMDB API to the database.
    
    Args:
        page (int): Page number for paginated TMDB results (default: 1).
    """
    logger.info(f"Syncing TMDB movies for page {page}")
    tmdb_data = TMDBUtils.get_popular_movies(page=page)
    if not tmdb_data.get('results'):
        logger.warning(f"No results from TMDB API for page {page}")
        return

    genre_map = TMDBUtils.get_genre_list()
    for movie_data in tmdb_data.get('results', []):
        try:
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
            logger.info(f"{'Created' if created else 'Updated'} movie: {movie.title} (TMDB ID: {movie.tmdb_id})")
        except Exception as e:
            logger.error(f"Error syncing movie {movie_data.get('title')} (TMDB ID: {movie_data.get('id')}): {str(e)}")