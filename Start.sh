#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"
if [[ ! -x .venv/bin/python ]]; then
  echo "Run bash Install.sh first." >&2
  exit 1
fi
export PYTHONIOENCODING=utf-8
exec .venv/bin/python installers/setup.py launch "$@"
