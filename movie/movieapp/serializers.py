from rest_framework import serializers
from .models import User, Genre, Movie, FavoriteMovie
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    favorite_movies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "favorite_movies"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

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
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = FavoriteMovie
        fields = ["id", "user", "movie", "movie_id", "added_at"]
        read_only_fields = ["user", "added_at"]

    def create(self, validated_data):
        # Check for existing FavoriteMovie entry
        user = self.context['request'].user
        movie = validated_data['movie']
        if FavoriteMovie.objects.filter(user=user, movie=movie).exists():
            raise ValidationError({"non_field_errors": ["This movie is already in your favorites."]})
        return super().create(validated_data)