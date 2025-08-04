# movieapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model extending AbstractUser."""
    email = models.EmailField(unique=True)
    favorite_movies = models.ManyToManyField("Movie", through="FavoriteMovie", related_name="favorited_by")

    def __str__(self):
        """Return the username as string representation."""
        return self.username

class Genre(models.Model):
    """Model representing a movie genre."""
    id = models.IntegerField(primary_key=True)  # Use TMDB genre ID as primary key
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        """Return the genre name as string representation."""
        return self.name

class Movie(models.Model):
    """Model representing a movie from TMDB."""
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    tmdb_id = models.IntegerField(unique=True, db_index=True)
    poster_path = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        """Return the movie title as string representation."""
        return self.title

class FavoriteMovie(models.Model):
    """Model representing a user's favorite movie."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("user", "movie")

    def __str__(self):
        """Return string representation of user and movie."""
        return f"{self.user.username} - {self.movie.title}"