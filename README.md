# 🎬 Movie Recommendation API

A RESTful API built with Django REST Framework and Python 3. It enables users to **register**, **log in**, **browse movies**, and **manage favorite movies**, integrating data from [The Movie Database (TMDB)](https://www.themoviedb.org/) and using **JWT authentication** with **Redis caching** for optimized performance.

---

## 🚀 Features

- User Registration & Authentication (JWT)
- Browse Movies (via TMDB API)
- Add / Remove Favorite Movies
- Redis Caching for Performance
- PostgreSQL for Production
- Secure Deployment Configuration

---

## 📦 Setup

### ✅ Prerequisites

- Python 3.8+
- Django 5.2
- Django REST Framework
- PostgreSQL (recommended)
- Redis
- TMDB API Key

### 📥 Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd movie-app
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   **requirements.txt:**
   ```txt
   django==5.2
   djangorestframework==3.15
   djangorestframework-simplejwt==5.3
   django-redis==5.4
   psycopg2-binary==2.9
   requests==2.31
   ```

3. **Configure Environment Variables**

   Create a `.env` file:
   ```env
   SECRET_KEY=your-django-secret-key
   TMDB_API_KEY=your-tmdb-api-key
   REDIS_URL=redis://localhost:6379/1
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Start Redis**
   ```bash
   redis-server
   ```

---

## 🔐 Authentication

JWT-based authentication using `djangorestframework-simplejwt`.

### 🔑 Obtain Token

**POST** `/api/token/`

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "favorite_movies": [1, 2]
  }
}
```

### 🔄 Refresh Token

**POST** `/api/token/refresh/`

**Request:**
```json
{
  "refresh": "string"
}
```

**Response:**
```json
{
  "access": "string"
}
```

### 🔐 Authorization Header

```http
Authorization: Bearer <access_token>
```

---

## 📚 API Endpoints

### 👤 User Registration

**POST** `/api/register/`

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "favorite_movies": []
}
```

---

### 🎞️ List Movies

**GET** `/api/movies/?page=1`

- Public access
- Supports pagination

**Response:**
```json
{
  "count": 100,
  "next": "url",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Inception",
      "release_date": "2010-07-16",
      "description": "A mind-bending thriller...",
      "poster_path": "url"
    }
  ]
}
```

---

### 🎬 Get Movie Details

**GET** `/api/movies/<id>/`

- Public access

**Response:**
```json
{
  "id": 1,
  "title": "Inception",
  "release_date": "2010-07-16",
  "description": "A mind-bending thriller...",
  "poster_path": "url",
  "genres": [{ "id": 1, "name": "Sci-Fi" }],
  "runtime": 148,
  "vote_average": 8.8,
  "vote_count": 10000,
  "overview": "A thief who steals corporate secrets...",
  "backdrop_path": "url"
}
```

---

### ⭐ List Favorite Movies

**GET** `/api/favorite-movies/?page=1`

- Requires authentication

**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "movie": {
        "id": 1,
        "title": "Inception",
        "release_date": "2010-07-16",
        "description": "A mind-bending thriller...",
        "poster_path": "url"
      },
      "added_at": "2024-08-07T12:00:00Z"
    }
  ]
}
```

---

### ➕ Add Favorite Movie

**POST** `/api/favorite-movies/`

**Request:**
```json
{
  "movie_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "movie": { ... },
  "added_at": "2024-08-07T12:00:00Z"
}
```

---

### ❌ Remove Favorite Movie

**DELETE** `/api/favorite-movies/<id>/`

- Response: `204 No Content`

---

## 🧩 Models

### User
- `id`: integer
- `username`: string
- `email`: string
- `favorite_movies`: array of movie IDs

### Movie
- `id`, `title`, `release_date`, `description`, `poster_path`, `tmdb_id`, `genres`

### FavoriteMovie
- `id`, `user`, `movie`, `added_at`

---

## 🚀 Caching

- Redis caching enabled for `GET /api/favorite-movies/` (15 minutes).
- Cache key: `favorite_movie_list_<user_id>_page_<page>`
- Automatically invalidated on add/delete operations.

---

## ⚠️ Error Handling

| Code | Meaning           | Example Response                                     |
|------|-------------------|------------------------------------------------------|
| 400  | Bad Request       | `{"detail": "Invalid page."}`                        |
| 401  | Unauthorized      | `{"detail": "Authentication credentials were not provided."}` |
| 404  | Not Found         | `{"detail": "Not found."}`                           |
| 429  | Too Many Requests | `{"detail": "Rate limit exceeded."}`                 |
| 500  | Server Error      | `{"detail": "Server error. Please try again."}`      |

---

## 🛡 Deployment

### Security Settings
- Store secrets in `.env`
- Set `DEBUG = False`
- Use `HTTPS` and secure cookies

### Database
- PostgreSQL recommended

### Redis
- Use `django-redis` for caching

### Static Files
```bash
python manage.py collectstatic
```

### Gunicorn + Nginx
```bash
gunicorn --workers 3 movieapp.wsgi:application
```

---

## 🧪 Testing (curl)

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/register/ -H "Content-Type: application/json" -d '{"username": "testuser", "email": "test@example.com", "password": "test1234"}'

# Login
curl -X POST http://127.0.0.1:8000/api/token/ -H "Content-Type: application/json" -d '{"username": "testuser", "password": "test1234"}'

# Get Favorites
curl -X GET http://127.0.0.1:8000/api/favorite-movies/?page=1 -H "Authorization: Bearer <access_token>"

# Add Favorite
curl -X POST http://127.0.0.1:8000/api/favorite-movies/ -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" -d '{"movie_id": 1}'

# Remove Favorite
curl -X DELETE http://127.0.0.1:8000/api/favorite-movies/1/ -H "Authorization: Bearer <access_token>"
```

---

## 🧠 Debugging

```bash
# View logs
python manage.py runserver

# Django shell
python manage.py shell

# Clear Redis
redis-cli FLUSHALL
```

---

## 📌 Notes

- TMDB integration requires a valid `TMDB_API_KEY`.
- Redis improves performance by caching frequent reads.
- Secure your production setup with HTTPS and cookie security.