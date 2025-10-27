#!/bin/bash

echo "${0}: Starting development server."

python3 manage.py makemigrations
python3 manage.py migrate

python3 manage.py collectstatic --no-input
python3 manage.py runserver 0.0.0.0:8000

