#!/bin/bash

# echo "${0}: running migrations."

python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py collectstatic --no-input
python3 -m gunicorn barodybroject.wsgi:application --bind 0.0.0.0:80
# python3 manage.py runserver 0.0.0.0:8000

# exec jekyll serve --config _config.yml --host 0.0.0.0 --port 4002

