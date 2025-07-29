from django.core.management.base import BaseCommand
from movieapp.models import Genre, Movie, FavoriteMovie
from django.contrib.auth import get_user_model
from faker import Faker
import random

class Command(BaseCommand):
      help = "Seeds the database with a large amount of sample data"

      def handle(self, *args, **options):
          fake = Faker()
          User = get_user_model()

          # Create or update multiple users
          users = []
          for i in range(2):  # Create 2 users
              username = f"testuser{i}"
              email = f"testuser{i}@example.com"
              user, created = User.objects.get_or_create(
                  username=username,
                  defaults={"email": email, "password": f"testpass{i}123"}
              )
              if not created:
                  user.email = email
                  user.set_password(f"testpass{i}123")
                  user.save()
              else:
                  user.set_password(f"testpass{i}123")
                  user.save()
              users.append(user)

          # Create 20 unique genres
          genres = [Genre.objects.get_or_create(name=fake.word().capitalize())[0] for _ in range(20)]

          # Create 100 movies with bulk creation
          movies_data = [
              Movie(
                  title=fake.sentence(nb_words=3).replace(".", ""),
                  description=fake.paragraph(),
                  release_date=fake.date_between(start_date="-10y", end_date="today"),
                  tmdb_id=random.randint(1000, 9999),
                  poster_path=fake.url()
              ) for _ in range(100)
          ]
          movies = Movie.objects.bulk_create(movies_data)
          for movie in movies:
              movie.genres.set(random.sample(genres, random.randint(1, 3)))

          # Create 200 unique favorite movie entries with bulk creation
          unique_combinations = set()
          while len(unique_combinations) < 200:
              user = random.choice(users)
              movie = random.choice(movies)
              combination = (user.id, movie.id)
              unique_combinations.add(combination)
          favorite_data = [
              FavoriteMovie(user=next(u for u in users if u.id == comb[0]), movie=next(m for m in movies if m.id == comb[1]), added_at=fake.date_time_between(start_date="-2y", end_date="now"))
              for comb in unique_combinations
          ]
          FavoriteMovie.objects.bulk_create(favorite_data)

          self.stdout.write(self.style.SUCCESS("Database seeded with 2 users, 20 genres, 100 movies, and 200 unique favorite entries"))