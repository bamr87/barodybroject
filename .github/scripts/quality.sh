#!/usr/bin/env bash
set -euo pipefail

command=${1:-lint}

case "$command" in
  lint)
    black --check --diff src/
    isort --profile=black --check-only --diff src/
    # flake8 removed: redundant with ruff (pyflakes/pycodestyle rule coverage).
    ruff check src/
    # bandit is report-only (matches the json invocation above and the
    # safety/pip-audit report artifacts); findings land in bandit-report.json.
    bandit -r src/ -f json -o bandit-report.json || true
    bandit -r src/ -f txt || true
    ;;
  dependency-scan)
    # Audit the dependencies this project DECLARES, not whatever happens to be
    # installed in the interpreter.
    #
    # Scope: src/requirements.txt — the application's runtime dependencies, and
    # the only set whose advisories should be able to block a merge. Dev and
    # CI-toolchain packages are deliberately out of scope: an advisory against a
    # linter or a scanner is not a risk to what this project ships, and gating
    # on one blocks merges nobody can unblock.
    #
    # Without -r, safety and pip-audit audit the whole environment. In the
    # `quality` job that environment is installed by python-install.sh lint +
    # security, and src/requirements.txt only arrives three steps LATER — so the
    # unscoped form could never report an advisory against Django, openai,
    # boto3 or psycopg2, while it did fail the build on nltk, a transitive
    # dependency of safety itself, for an advisory with no patched version.
    # Passing -r makes the audited set a declared artifact instead of a side
    # effect of step ordering, and keeps it correct if the job is reordered.
    #
    # The --json/--output calls write the report artifacts and may swallow their
    # exit code; the bare calls are the gate and must keep their teeth.
    cd src
    safety check -r requirements.txt --json > safety-report.json 2>/dev/null || true
    safety check -r requirements.txt
    pip-audit --desc -r requirements.txt --format=json --output=pip-audit-report.json || true
    pip-audit --desc -r requirements.txt
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