# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create staticfiles directory
RUN mkdir -p staticfiles && \
    python manage.py collectstatic --noinput || true

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn smarten.asgi:application --worker-class uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:8000 --timeout 120"]