release: python manage.py migrate
web: gunicorn mp.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 