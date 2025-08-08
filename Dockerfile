# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "movies.wsgi:application"]