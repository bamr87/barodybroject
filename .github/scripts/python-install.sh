#!/usr/bin/env bash
set -euo pipefail

mode=${1:-runtime}

python -m pip install --upgrade pip

case "$mode" in
  runtime)
    (cd src && pip install -r requirements.txt)
    ;;
  test|e2e)
    (cd src && pip install -r requirements.txt)
    pip install coverage pytest-cov pytest-django pytest-playwright
    ;;
  lint)
    pip install black isort flake8 ruff bandit
    ;;
  security)
    pip install safety pip-audit
    ;;
  quality)
    (cd src && pip install -r requirements.txt)
    pip install pylint mypy xenon radon
    ;;
  maintenance)
    pip install pip-check pip-outdated safety
    ;;
  update-dependencies)
    pip install pip-check
    (cd src && pip install --upgrade -r requirements.txt && pip freeze > requirements-updated.txt)
    (cd src && pip-check) || echo "Some dependency conflicts were detected."
    ;;
  *)
    echo "Unknown Python dependency mode: $mode"
    exit 1
    ;;
esac