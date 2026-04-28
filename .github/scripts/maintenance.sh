#!/usr/bin/env bash
set -euo pipefail

command=${1:-}
dev_compose=${DEV_COMPOSE:-.devcontainer/docker-compose_dev.yml}

write_dev_env() {
  cat > .env <<EOF
POSTGRES_USER=test_user
POSTGRES_DB=test_db
POSTGRES_PASSWORD=test_password
DB_HOST=barodydb
DB_USERNAME=test_user
DB_NAME=test_db
DB_PASSWORD=test_password
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing
DEBUG=True
RUNNING_IN_PRODUCTION=False
PYTHONPATH=/workspace/src:/workspace
PYTHONUNBUFFERED=1
SECRET_KEY=ci-test-key-not-for-production
EOF
}

collect_infrastructure_logs() {
  mkdir -p artifacts/logs

  if [[ -d logs ]]; then
    cp -r logs/* artifacts/logs/ 2>/dev/null || true
  fi

  docker compose -f "$dev_compose" logs --no-color > artifacts/logs/docker-compose.log 2>&1 || true
  docker compose -f "$dev_compose" logs --no-color python > artifacts/logs/python-container.log 2>&1 || true
  docker compose -f "$dev_compose" logs --no-color barodydb > artifacts/logs/postgres-container.log 2>&1 || true
  docker compose -f "$dev_compose" logs --no-color jekyll > artifacts/logs/jekyll-container.log 2>&1 || true
  docker system df > artifacts/logs/docker-system-info.log 2>&1 || true
  docker compose -f "$dev_compose" ps > artifacts/logs/container-status.log 2>&1 || true
}

cleanup_dev() {
  docker compose -f "$dev_compose" down -v --remove-orphans || true
}

case "$command" in
  dependency-check)
    mkdir -p reports
    cd src
    pip list
    pip-check
    pip list --outdated || true
    safety check --json --output safety-report.json || true
    safety check
    cd ..

    {
      echo "# Dependency Health Report"
      echo
      echo "Generated: $(date -u)"
      echo
      echo "## Outdated Dependencies"
      echo '```'
      (cd src && pip list --outdated) || true
      echo '```'
      echo
      echo "## Security Issues"
      if [[ -f src/safety-report.json ]]; then
        echo '```json'
        cat src/safety-report.json
        echo '```'
      else
        echo "No safety report was generated."
      fi
    } > reports/dependency-report.md
    ;;
  update-dependencies)
    bash .github/scripts/python-install.sh update-dependencies
    ;;
  container-environment)
    config=${2:-development}

    case "$config" in
      development)
        trap cleanup_dev EXIT
        write_dev_env
        docker compose -f "$dev_compose" up -d barodydb
        timeout 60 bash -c "until docker compose -f '$dev_compose' exec -T barodydb pg_isready -U test_user -d test_db; do sleep 2; done"
        docker compose -f "$dev_compose" run --rm \
          -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing \
          -e SECRET_KEY=ci-test-key-not-for-production \
          python python manage.py check
        ;;
      production)
        trap 'docker compose -f docker-compose.yml down -v --remove-orphans || true' EXIT
        cat > .env <<EOF
POSTGRES_USER=prod_user
POSTGRES_DB=prod_db
POSTGRES_PASSWORD=prod_password
DB_HOST=barodydb
DB_USERNAME=prod_user
DB_NAME=prod_db
DB_PASSWORD=prod_password
DJANGO_SETTINGS_MODULE=barodybroject.settings.production
DEBUG=False
RUNNING_IN_PRODUCTION=True
SECRET_KEY=production-test-key-not-for-real-production
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_PROD_PORT=8000
EOF
        docker compose -f docker-compose.yml up -d barodydb web-prod
        timeout 90 bash -c 'until curl -fsS http://localhost:8000/ > /dev/null; do sleep 3; done'
        docker compose -f docker-compose.yml ps
        docker compose -f docker-compose.yml logs --no-color
        ;;
      *)
        echo "Unknown container environment: $config"
        exit 1
        ;;
    esac
    ;;
  infrastructure-test)
    trap 'collect_infrastructure_logs; [[ "${SKIP_CLEANUP:-false}" == "true" ]] || cleanup_dev' EXIT
    write_dev_env
    mkdir -p logs artifacts/logs
    docker compose -f "$dev_compose" build --parallel
    docker compose -f "$dev_compose" up -d
    timeout 60 bash -c "until docker compose -f '$dev_compose' exec -T barodydb pg_isready -U test_user -d test_db; do sleep 2; done"
    timeout 60 bash -c "until docker compose -f '$dev_compose' exec -T python echo Ready; do sleep 2; done"

    script_args=(--ci-mode)
    [[ "${VERBOSE:-false}" == "true" ]] && script_args+=(--verbose)
    [[ "${SKIP_CLEANUP:-false}" == "true" ]] && script_args+=(--skip-cleanup)
    ./scripts/test-infrastructure.sh "${script_args[@]}"
    ;;
  cleanup)
    docker compose down -v || true
    docker compose -f "$dev_compose" down -v || true
    docker system prune -f
    docker volume prune -f
    docker system df
    docker compose config -q
    docker compose -f "$dev_compose" config -q
    find . -type f -size +10M -not -path "./.git/*" -not -path "./htmlcov/*" || true
    find . -name "*.pyc" -o -name "__pycache__" -o -name "*.log" -not -path "./.git/*" || true
    ;;
  report)
    mkdir -p reports
    {
      echo "# Maintenance Health Report"
      echo
      echo "Generated: $(date -u)"
      echo
      echo "## Job Results"
      echo "- Dependency Check: ${DEPENDENCY_RESULT:-skipped}"
      echo "- Container Environments: ${CONTAINER_RESULT:-skipped}"
      echo "- Infrastructure Test: ${INFRASTRUCTURE_RESULT:-skipped}"
      echo
      echo "## Recommendations"
      echo "- Review dependency and security reports."
      echo "- Run full CI before merging dependency update pull requests."
      echo "- Review infrastructure artifacts when infrastructure tests fail."
    } > reports/maintenance-health.md
    ;;
  *)
    echo "Usage: $0 {dependency-check|update-dependencies|container-environment|infrastructure-test|cleanup|report}"
    exit 1
    ;;
esac