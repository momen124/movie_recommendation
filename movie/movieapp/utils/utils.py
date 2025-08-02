import requests
from django.conf import settings

class TMDBUtils:
    BASE_URL = "https://api.themoviedb.org/3"
    API_KEY = settings.TMDB_API_KEY

    @staticmethod
    def get_popular_movies(page=1):
        url = f"{TMDBUtils.BASE_URL}/movie/popular"
        params = {"api_key": TMDBUtils.API_KEY, "page": page}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_movie_details(movie_id):
        url = f"{TMDBUtils.BASE_URL}/movie/{movie_id}"
        params = {"api_key": TMDBUtils.API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()