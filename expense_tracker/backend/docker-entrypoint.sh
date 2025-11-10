#!/bin/bash
# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start daphne to serve both API and frontend
echo "Starting server..."
exec daphne -b 0.0.0.0 -p 8000 expense_tracker.asgi:application


