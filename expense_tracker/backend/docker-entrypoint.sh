#!/bin/bash
set -e

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting services with Supervisor..."
echo "  - Gunicorn (Django web server)"
echo "  - Telegram Polling (payment confirmation bot)"

# Create log directory for supervisor
mkdir -p /var/log/supervisor

# Start supervisor (runs both gunicorn and telegram polling)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
