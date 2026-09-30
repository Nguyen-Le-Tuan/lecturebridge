#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
  echo "LectureBridge supports Linux x86-64 in this release." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "Install curl, then install uv from https://docs.astral.sh/uv/." >&2
    exit 1
  fi
  echo "uv was not found; installing it with Astral's official installer."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

uv sync --locked
uv run lecturebridge-models download --model distil-large-v3.5

echo
echo "Running readiness checks. Tailscale must already be installed and signed in."
uv run lecturebridge-preflight --device auto
