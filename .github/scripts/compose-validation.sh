#!/usr/bin/env bash
set -euo pipefail

command=${1:-validate}
service=${2:-}
dev_compose=${DEV_COMPOSE:-.devcontainer/docker-compose_dev.yml}

write_env() {
  local prefix=${1:-test}

  cat > .env <<EOF
POSTGRES_USER=${prefix}_user
POSTGRES_DB=${prefix}_db
POSTGRES_PASSWORD=${prefix}_password
DB_HOST=barodydb
DB_USERNAME=${prefix}_user
DB_NAME=${prefix}_db
DB_PASSWORD=${prefix}_password
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing
DEBUG=True
RUNNING_IN_PRODUCTION=False
PYTHONPATH=/workspace/src
PYTHONUNBUFFERED=1
SECRET_KEY=ci-test-key-not-for-production
EOF
}

cleanup_dev() {
  docker compose -f "$dev_compose" down -v --remove-orphans || true
}

wait_for_dev_database() {
  timeout 60 bash -c "until docker compose -f '$dev_compose' exec -T barodydb pg_isready -U test_user -d test_db; do sleep 2; done"
}

case "$command" in
  validate)
    docker compose -f "$dev_compose" config --quiet
    docker compose config --quiet
    ;;
  smoke)
    trap cleanup_dev EXIT
    write_env test
    docker compose -f "$dev_compose" up -d barodydb
    wait_for_dev_database
    docker compose -f "$dev_compose" run --rm \
      -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing \
      -e SECRET_KEY=ci-test-key-not-for-production \
      python bash -lc "python manage.py check --deploy && python manage.py migrate --noinput"
    ;;
  build-service)
    if [[ -z "$service" ]]; then
      echo "build-service requires a service name."
      exit 1
    fi

    trap cleanup_dev EXIT
    write_env build
    docker compose -f "$dev_compose" build "$service"

    if [[ "$service" == "python" ]]; then
      docker compose -f "$dev_compose" up -d barodydb
      timeout 60 bash -c "until docker inspect --format='{{.State.Health.Status}}' \$(docker compose -f '$dev_compose' ps -q barodydb) | grep -q healthy; do sleep 2; done"
      docker compose -f "$dev_compose" run --rm "$service" python --version
    elif [[ "$service" == "jekyll" ]]; then
      docker compose -f "$dev_compose" run --rm "$service" jekyll --version
    else
      echo "Unsupported service for build validation: $service"
      exit 1
    fi
    ;;
  build-production-image)
    image_tag=${service:-barodybroject:security-scan}
    docker build --tag "$image_tag" -f src/Dockerfile src
    ;;
  *)
    echo "Unknown compose validation command: $command"
    exit 1
    ;;
esac