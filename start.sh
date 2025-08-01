#!/bin/bash
echo "Starting SeaMap application..."
python manage.py collectstatic --noinput
python manage.py migrate
exec gunicorn seamap.wsgi:application --bind 0.0.0.0:$PORT --workers 3
