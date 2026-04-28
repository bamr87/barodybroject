#!/usr/bin/env bash
set -euo pipefail

mode=${1:-test}

packages=(
  libpq-dev
  postgresql-client
)

case "$mode" in
  django|test|e2e|quality)
    packages+=(
      build-essential
      pkg-config
      libcairo2-dev
      libgirepository1.0-dev
      libglib2.0-dev
      python3-dev
      python3-cairo
      python3-gi
      python3-gi-cairo
      libcairo-gobject2
      gobject-introspection
    )
    ;;
  minimal)
    ;;
  *)
    echo "Unknown system dependency mode: $mode"
    exit 1
    ;;
esac

sudo apt-get update
sudo apt-get install -y "${packages[@]}"