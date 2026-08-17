# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create staticfiles directory
RUN mkdir -p staticfiles && \\
    python manage.py collectstatic --noinput || true

# Run gunicorn with daphne for async support
CMD ["gunicorn", "smarten.asgi:application", \\
     "--worker-class", "uvicorn.workers.UvicornWorker", \\
     "--workers", "2", \\
     "--bind", "0.0.0.0:8000", \\
     "--timeout", "120"]
