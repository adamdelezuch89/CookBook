# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE cookbook.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create directory structure
RUN mkdir -p /app/staticfiles /app/media

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a script to handle startup tasks
RUN echo '#!/bin/bash\n\
# Create static directory if it doesnt exist\n\
mkdir -p /app/staticfiles\n\
# Collect static files\n\
python manage.py collectstatic --noinput\n\
# Run migrations\n\
python manage.py migrate\n\
# Start gunicorn\n\
exec gunicorn cookbook.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Set proper permissions
RUN chown -R www-data:www-data /app/staticfiles /app/media

# Change the CMD to use the entrypoint script
CMD ["/app/entrypoint.sh"] 