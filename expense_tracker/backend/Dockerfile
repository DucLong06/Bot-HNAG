FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy Entrypoint
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Run daphne by default
CMD ["sh", "/app/docker-entrypoint.sh"]
