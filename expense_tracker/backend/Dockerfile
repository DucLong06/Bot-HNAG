FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including cron
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]