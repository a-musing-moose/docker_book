#! /bin/sh

# Start Django
cd /app
/venv/bin/python /app/manage.py migrate --noinput
/venv/bin/uwsgi --ini /app/uwsgi.ini 2>&1
