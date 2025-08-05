# movieapp/serializers.py
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema_field
from movieapp.models import User, Genre, Movie, FavoriteMovie

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with favorite movies."""
    favorite_movies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "favorite_movies"]
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'help_text': 'Username for the user'},
            'email': {'help_text': 'Email address of the user'},
            'favorite_movies': {'help_text': 'List of favorite movie IDs'},
        }

    def create(self, validated_data):
        """Create a new user with hashed password.
        
        Args:
            validated_data (dict): Validated user data.
        
        Returns:
            User: Created user instance.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        """Update an existing user, including password if provided.
        
        Args:
            instance (User): User instance to update.
            validated_data (dict): Validated data for update.
        
        Returns:
            User: Updated user instance.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model."""
    class Meta:
        model = Genre
        fields = ["id", "name"]
        extra_kwargs = {
            'id': {'help_text': 'TMDB genre ID'},
            'name': {'help_text': 'Genre name'},
        }

class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model with genres."""
    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "description", "release_date", "genres", "tmdb_id", "poster_path"]
        extra_kwargs = {
            'tmdb_id': {'help_text': 'TMDB movie ID'},
            'title': {'help_text': 'Movie title'},
            'description': {'help_text': 'Movie overview'},
            'release_date': {'help_text': 'Release date of the movie'},
            'poster_path': {'help_text': 'URL to movie poster image'},
        }

class FavoriteMovieSerializer(serializers.ModelSerializer):
    """Serializer for FavoriteMovie model with movie details."""
    user = serializers.ReadOnlyField(source="user.username")
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = FavoriteMovie
        fields = ["id", "user", "movie", "movie_id", "added_at"]
        read_only_fields = ["user", "added_at"]
        extra_kwargs = {
            'movie_id': {'help_text': 'ID of the movie to favorite'},
            'added_at': {'help_text': 'Timestamp when movie was favorited'},
        }

    def create(self, validated_data):
        """Create a new favorite movie entry, checking for duplicates.
        
        Args:
            validated_data (dict): Validated data including movie ID.
        
        Returns:
            FavoriteMovie: Created favorite movie instance.
        
        Raises:
            ValidationError: If the movie is already favorited by the user.
        """
        user = self.context['request'].user
        movie = validated_data['movie']
        if FavoriteMovie.objects.filter(user=user, movie=movie).exists():
            raise ValidationError({"non_field_errors": ["This movie is already in your favorites."]})
        return super().create(validated_data)