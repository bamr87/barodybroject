#!/usr/bin/env bash
set -euo pipefail

db_host=${DB_HOST:-localhost}
db_user=${DB_USERNAME:-postgres}
db_password=${DB_PASSWORD:-postgres}
e2e_db=${E2E_DB_NAME:-test_barodydb_e2e}
e2e_schema=${E2E_DB_SCHEMA:-e2e}
e2e_username=${E2E_USERNAME:-e2e_user}
e2e_email=${E2E_EMAIL:-e2e_user@example.com}
e2e_password=${E2E_PASSWORD:-e2e_password}

python -m playwright install --with-deps chromium

export PGPASSWORD="$db_password"
psql -h "$db_host" -U "$db_user" -d postgres -c "CREATE DATABASE $e2e_db;" || true
psql -h "$db_host" -U "$db_user" -d "$e2e_db" -c "CREATE SCHEMA IF NOT EXISTS $e2e_schema;"

export DB_NAME="$e2e_db"
export DB_SCHEMA="$e2e_schema"
export E2E_USERNAME="$e2e_username"
export E2E_EMAIL="$e2e_email"
export E2E_PASSWORD="$e2e_password"

python src/manage.py migrate --noinput
python src/manage.py ensure_e2e_user --is-staff

nohup python src/manage.py runserver 0.0.0.0:8000 --noreload > server.log 2>&1 &

for _ in {1..30}; do
  if curl -fsS http://localhost:8000/ > /dev/null; then
    echo "Django E2E server is ready."
    break
  fi
  sleep 1
done

if ! curl -fsS http://localhost:8000/ > /dev/null; then
  echo "Django E2E server failed to start."
  tail -200 server.log || true
  exit 1
fi

export E2E_BASE_URL=http://localhost:8000
cd src
python -m pytest -m e2e --browser chromium