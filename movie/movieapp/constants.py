# movieapp/constants.py
"""Constants for the movie recommendation project."""
TMDB_BASE_URL = "https://api.themoviedb.org/3"
CACHE_TIMEOUT = 60 * 15  # 15 minutes
PAGE_SIZE = 20
GENRE_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours