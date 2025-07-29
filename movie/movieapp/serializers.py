from rest_framework import serializers
from .models import User, Genre, Movie, FavoriteMovie

class UserSerializer(serializers.ModelSerializer):
    favorite_movies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "favorite_movies"]

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]

class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_date", "genres", "tmdb_id", "poster_path"]

class FavoriteMovieSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    movie = MovieSerializer()

    class Meta:
        model = FavoriteMovie
        fields = ["id", "user", "movie", "added_at"]