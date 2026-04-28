#!/usr/bin/env bash
set -euo pipefail

command=${1:-lint}

case "$command" in
  lint)
    black --check --diff src/
    isort --profile=black --check-only --diff src/
    ruff check src/
    flake8 src/ --max-line-length=88 --extend-ignore=E203,W503
    bandit -r src/ -f json -o bandit-report.json || true
    bandit -r src/ -f txt
    ;;
  dependency-scan)
    cd src
    safety check --json --output safety-report.json || true
    safety check
    pip-audit --desc --format=json --output=pip-audit-report.json || true
    pip-audit --desc
    ;;
  metrics)
    cd src
    pylint parodynews/ --output-format=json:pylint-report.json,text:pylint-report.txt || true
    cat pylint-report.txt
    mypy parodynews/ --ignore-missing-imports --json-report mypy-report || true
    xenon parodynews/ --max-absolute B --max-modules A --max-average A || true
    radon cc parodynews/ -j > radon-cc.json
    radon mi parodynews/ -j > radon-mi.json
    radon raw parodynews/ -j > radon-raw.json
    radon cc parodynews/
    radon mi parodynews/
    ;;
  environment)
    docker compose config -q
    docker compose -f .devcontainer/docker-compose_dev.yml config -q

    if [[ -f azure.yaml ]]; then
      grep -q "^  src:" azure.yaml
    elif [[ -f src/azure.yaml ]]; then
      grep -q "^  src:" src/azure.yaml
    else
      echo "No azure.yaml found."
      exit 1
    fi

    docker run --rm -v "$PWD:/pwd" trufflesecurity/trufflehog:3.63.5 filesystem /pwd --json > secrets-scan.json || true
    if [[ -s secrets-scan.json ]]; then
      echo "Potential secrets detected. Review the secrets-scan artifact."
    else
      echo "No potential secrets detected."
    fi
    ;;
  *)
    echo "Unknown quality command: $command"
    exit 1
    ;;
esac