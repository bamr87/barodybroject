#!/usr/bin/env bash
set -euo pipefail

marker=${PYTEST_MARKER:-not e2e}

cd src

python -m pytest -m "$marker" --cov-report=xml --cov-report=term-missing