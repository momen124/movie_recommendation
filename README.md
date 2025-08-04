# movie_recommendation
Movie Website API Documentation
Overview
The Movie Website API is a RESTful API built with Django REST Framework (DRF) and Python 3. It allows users to register, log in, browse movies, and manage a list of favorite movies. The API integrates with The Movie Database (TMDB) for movie data and uses JSON Web Tokens (JWT) for authentication. Redis caching optimizes performance for frequently accessed endpoints.
This documentation covers the API’s endpoints, authentication, request/response formats, and deployment considerations. The base URL for all endpoints is /api/.
Setup
Prerequisites

Python 3.8+
Django 5.2
Django REST Framework
Redis (for caching)
PostgreSQL (recommended for production)
TMDB API key

Installation

Clone the Repository:
git clone <repository-url>
cd movie-app


Install Dependencies:
pip install -r requirements.txt

Example requirements.txt:
django==5.2
djangorestframework==3.15
djangorestframework-simplejwt==5.3
django-redis==5.4
psycopg2-binary==2.9
requests==2.31


Configure Environment Variables:Create a .env file:
SECRET_KEY=your-django-secret-key
TMDB_API_KEY=your-tmdb-api-key
REDIS_URL=redis://localhost:6379/1
DATABASE_URL=postgresql://user:password@localhost:5432/dbname


Run Migrations:
python manage.py migrate


Start Development Server:
python manage.py runserver


Start Redis:
redis-server



Authentication
The API uses JWT for authentication via djangorestframework-simplejwt. Users must authenticate to access protected endpoints (/api/favorite-movies/, /api/movies/<id>/).
Obtaining a Token

Endpoint: POST /api/token/
Description: Authenticates a user and returns access and refresh tokens.
Request:{
  "username": "string",
  "password": "string"
}


Response (200 OK):{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": number,
    "username": "string",
    "email": "string",
    "favorite_movies": [number]
  }
}


Errors:
400 Bad Request: Invalid credentials.{"detail": "No active account found with the given credentials"}


429 Too Many Requests: Rate limit exceeded.



Refreshing a Token

Endpoint: POST /api/token/refresh/
Description: Refreshes an expired access token using a refresh token.
Request:{
  "refresh": "string"
}


Response (200 OK):{
  "access": "string"
}


Errors:
401 Unauthorized: Invalid or expired refresh token.{"detail": "Token is invalid or expired"}





Authorization Header
Protected endpoints require the Authorization header:
Authorization: Bearer <access_token>

Endpoints
User Registration

Endpoint: POST /api/register/
Description: Creates a new user account.
Request:{
  "username": "string",
  "email": "string",
  "password": "string"
}


Response (201 Created):{
  "id": number,
  "username": "string",
  "email": "string",
  "favorite_movies": []
}


Errors:
400 Bad Request: Invalid or missing fields, duplicate username/email.{
  "username": ["A user with that username already exists."],
  "email": ["This field must be unique."]
}





List Movies

Endpoint: GET /api/movies/?page=<number>
Description: Retrieves a paginated list of movies from TMDB.
Authentication: Optional (public access).
Query Parameters:
page (optional, default=1): Page number for pagination.


Response (200 OK):{
  "count": number,
  "next": "string | null",
  "previous": "string | null",
  "results": [
    {
      "id": number,
      "title": "string",
      "release_date": "YYYY-MM-DD",
      "description": "string",
      "poster_path": "string | null"
    }
  ]
}


Errors:
400 Bad Request: Invalid page number.{"detail": "Invalid page."}





Get Movie Details

Endpoint: GET /api/movies/<id>/
Description: Retrieves detailed information for a specific movie.
Authentication: Optional (public access).
Response (200 OK):{
  "id": number,
  "title": "string",
  "release_date": "YYYY-MM-DD",
  "description": "string",
  "poster_path": "string | null",
  "genres": [
    {
      "id": number,
      "name": "string"
    }
  ],
  "runtime": number | null,
  "vote_average": number | null,
  "vote_count": number | null,
  "overview": "string",
  "backdrop_path": "string | null"
}


Errors:
404 Not Found: Movie does not exist.{"detail": "Not found."}





List Favorite Movies

Endpoint: GET /api/favorite-movies/?page=<number>
Description: Retrieves a paginated list of the authenticated user’s favorite movies.
Authentication: Required.
Query Parameters:
page (optional, default=1): Page number for pagination.


Response (200 OK):{
  "count": number,
  "next": "string | null",
  "previous": "string | null",
  "results": [
    {
      "id": number,
      "movie": {
        "id": number,
        "title": "string",
        "release_date": "YYYY-MM-DD",
        "description": "string",
        "poster_path": "string | null"
      },
      "added_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}


Errors:
401 Unauthorized: Missing or invalid token.{"detail": "Authentication credentials were not provided."}


400 Bad Request: Invalid page number.{"detail": "Invalid page."}





Add Favorite Movie

Endpoint: POST /api/favorite-movies/
Description: Adds a movie to the authenticated user’s favorites.
Authentication: Required.
Request:{
  "movie_id": number
}


Response (201 Created):{
  "id": number,
  "movie": {
    "id": number,
    "title": "string",
    "release_date": "YYYY-MM-DD",
    "description": "string",
    "poster_path": "string | null"
  },
  "added_at": "YYYY-MM-DDTHH:MM:SSZ"
}


Errors:
400 Bad Request: Movie already in favorites or invalid movie ID.{
  "non_field_errors": ["This movie is already in your favorites."],
  "movie_id": ["Invalid pk \"<id>\" - object does not exist."]
}


401 Unauthorized: Missing or invalid token.



Remove Favorite Movie

Endpoint: DELETE /api/favorite-movies/<id>/
Description: Removes a movie from the authenticated user’s favorites.
Authentication: Required.
Response (204 No Content):
No body returned.


Errors:
404 Not Found: Favorite movie ID does not exist.{"detail": "Not found."}


401 Unauthorized: Missing or invalid token.



Models
User

id: Integer (unique identifier)
username: String (unique, max 150 characters)
email: String (unique)
favorite_movies: Array of movie IDs (optional)

Movie

id: Integer (unique identifier)
title: String
release_date: Date (YYYY-MM-DD)
description: String
poster_path: String (optional, TMDB URL)
tmdb_id: Integer (TMDB identifier)
genres: Array of { id: number, name: string }

FavoriteMovie

id: Integer (unique identifier)
user: ForeignKey to User
movie: ForeignKey to Movie
added_at: DateTime (YYYY-MM-DDTHH:MM:SSZ)

Caching

The FavoriteMovieViewSet uses Redis caching (cache_page(60 * 15)) for GET /api/favorite-movies/.
Cache keys are invalidated on POST and DELETE operations using perform_create and perform_destroy.
Cache key format: favorite_movie_list_<user_id>_page_<page>.

Error Handling

400 Bad Request: Invalid request data.
401 Unauthorized: Missing or invalid authentication token.
404 Not Found: Resource not found (e.g., movie or favorite ID).
429 Too Many Requests: Rate limit exceeded.
500 Internal Server Error: Server-side issues (e.g., TMDB API failure).

Deployment
Follow the Django 5.2 Deployment Checklist for production.
Key Configurations

Secure Settings:
# settings.py
SECRET_KEY = 'your-secret-key'  # Store in environment variable
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']


Database:Use PostgreSQL:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


CORS:
CORS_ALLOWED_ORIGINS = ['https://your-frontend-domain.com']
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True


Static Files:
STATIC_ROOT = '/path/to/static/'

Run:
python manage.py collectstatic


Gunicorn and Nginx:
pip install gunicorn
gunicorn --workers 3 your_project_name.wsgi:application

server {
    listen 80;
    server_name your-domain.com;
    location /static/ {
        alias /path/to/static/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}


Redis:
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://your-redis-host:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}



Security Considerations

Use HttpOnly, Secure, and SameSite=Lax cookies for JWT tokens in production:class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.set_cookie(
            key='access_token',
            value=response.data['access'],
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=3600
        )
        response.set_cookie(
            key='refresh_token',
            value=response.data['refresh'],
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=86400
        )
        return response


Enable HTTPS in production.
Implement rate limiting with django-ratelimit or similar.

Testing
Test endpoints using curl or Postman.
Register
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "test1234"}'

Login
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test1234"}'

Get Favorites
curl -X GET http://127.0.0.1:8000/api/favorite-movies/?page=1 \
  -H "Authorization: Bearer <access_token>"

Add Favorite
curl -X POST http://127.0.0.1:8000/api/favorite-movies/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 1}'

Remove Favorite
curl -X DELETE http://127.0.0.1:8000/api/favorite-movies/<id>/ \
  -H "Authorization: Bearer <access_token>"

Debugging

Check Logs: Django logs (python manage.py runserver) show request status (e.g., 200, 401).
Verify Database:from movieapp.models import User, Movie, FavoriteMovie
User.objects.all().values('id', 'username', 'email')
Movie.objects.all().values('id', 'title', 'tmdb_id')
FavoriteMovie.objects.all().values('id', 'user__username', 'movie__title')


Clear Redis Cache:redis-cli FLUSHALL



Notes

The API integrates with TMDB for movie data. Ensure a valid TMDB_API_KEY is set.
Cache invalidation occurs on POST and DELETE for /api/favorite-movies/.
Frontend should handle 204 No Content responses for DELETE requests without attempting JSON parsing.
