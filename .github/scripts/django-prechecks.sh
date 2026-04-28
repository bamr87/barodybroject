#!/usr/bin/env bash
set -euo pipefail

cd src

python manage.py check --deploy
python manage.py showmigrations --plan
python manage.py check --deploy