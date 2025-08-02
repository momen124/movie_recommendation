import requests
from django.conf import settings

class TMDBUtils:
    BASE_URL = "https://api.themoviedb.org/3"
    API_KEY = settings.TMDB_API_KEY

    @staticmethod
    def get_popular_movies(page=1):
        try:
            url = f"{TMDBUtils.BASE_URL}/movie/popular"
            params = {"api_key": TMDBUtils.API_KEY, "page": page}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"TMDB API error (popular movies): {e}")
            return {'results': []}

    @staticmethod
    def get_movie_details(movie_id):
        try:
            url = f"{TMDBUtils.BASE_URL}/movie/{movie_id}"
            params = {"api_key": TMDBUtils.API_KEY}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"TMDB API error (movie details): {e}")
            return {}

    @staticmethod
    def get_genre_list():
        try:
            url = f"{TMDBUtils.BASE_URL}/genre/movie/list"
            params = {"api_key": TMDBUtils.API_KEY}
            response = requests.get(url, params=params)
            response.raise_for_status()
            genres = response.json().get('genres', [])
            return {genre['id']: genre['name'] for genre in genres}
        except requests.RequestException as e:
            print(f"TMDB API error (genre list): {e}")
            return {}