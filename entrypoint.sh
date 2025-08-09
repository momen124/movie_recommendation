#!/bin/sh
set -e
# Wait for database
until pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-movie_user}; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done
# Run migrations
python manage.py migrate --noinput
# Collect static files
python manage.py collectstatic --noinput
# Execute the command (e.g., gunicorn)
exec "$@"