from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
         email = models.EmailField(unique=True)
         favorite_movies = models.ManyToManyField("Movie", through="FavoriteMovie", related_name="favorited_by")

         def __str__(self):
             return self.username

class Genre(models.Model):
         name = models.CharField(max_length=100, unique=True)

         def __str__(self):
             return self.name

class Movie(models.Model):
         title = models.CharField(max_length=200)
         description = models.TextField()
         release_date = models.DateField()
         genres = models.ManyToManyField(Genre, related_name="movies")
         tmdb_id = models.IntegerField(unique=True)
         poster_path = models.URLField(max_length=500, blank=True, null=True)

         def __str__(self):
             return self.title

class FavoriteMovie(models.Model):
         user = models.ForeignKey(User, on_delete=models.CASCADE)
         movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
         added_at = models.DateTimeField(auto_now_add=True)

         class Meta:
             unique_together = ("user", "movie")

         def __str__(self):
             return f"{self.user.username} - {self.movie.title}"