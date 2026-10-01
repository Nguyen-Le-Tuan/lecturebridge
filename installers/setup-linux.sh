#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
mkdir -p .lecturebridge
exec > >(tee .lecturebridge/setup.log) 2>&1
trap 'echo "Setup stopped. Review .lecturebridge/setup.log and rerun bash Install.sh."' ERR
if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
  echo "This installer requires Ubuntu/Linux x86-64." >&2
  exit 1
fi
if [[ ! -f /etc/os-release ]]; then
  echo "Unable to identify the Linux distribution." >&2
  exit 1
fi
# shellcheck source=/dev/null
source /etc/os-release
if [[ "${ID:-}" != "ubuntu" && " ${ID_LIKE:-} " != *" ubuntu "* ]]; then
  echo "Automatic system setup supports Ubuntu and Ubuntu derivatives only." >&2
  exit 1
fi
: > .lecturebridge/installing
missing=()
for package in curl ca-certificates libgomp1; do
  if ! dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -qx 'install ok installed'; then
    missing+=("$package")
  fi
done
if (( ${#missing[@]} )); then
  echo "Installing required Ubuntu packages: ${missing[*]}"
  admin=()
  if (( EUID != 0 )); then
    if ! command -v sudo >/dev/null; then
      echo "sudo is required to install system prerequisites." >&2
      exit 1
    fi
    admin=(sudo)
  fi
  "${admin[@]}" apt-get update
  "${admin[@]}" apt-get install -y "${missing[@]}"
fi
uv_version=0.12.13
uv_dir="$project_dir/.tools/uv-$uv_version"
uv_exe="$uv_dir/uv"
mkdir -p "$uv_dir"
if [[ ! -x "$uv_exe" ]]; then
  archive="$uv_dir/uv.tar.gz"
  curl --fail --location --retry 3 --connect-timeout 20 \
    "https://github.com/astral-sh/uv/releases/download/$uv_version/uv-x86_64-unknown-linux-gnu.tar.gz" -o "$archive"
  echo "745765a3b6e360ad76743599ae5c42e9278c7edf8bbff9fc76d05bf2623a04dd  $archive" | sha256sum --check -
  tar -xzf "$archive" --strip-components=1 -C "$uv_dir" uv-x86_64-unknown-linux-gnu/uv
  rm "$archive"
fi
export UV_PYTHON_INSTALL_DIR="$project_dir/.tools/python"
export UV_PROJECT_ENVIRONMENT="$project_dir/.venv"
export UV_PYTHON_PREFERENCE=only-managed
export PYTHONIOENCODING=utf-8
"$uv_exe" python install --no-bin 3.12
if [[ ! -x .venv/bin/python ]]; then
  "$uv_exe" venv --python 3.12 .venv
fi
.venv/bin/python installers/setup.py plan "$@"
"$uv_exe" sync --locked --no-dev --python 3.12
.venv/bin/python installers/setup.py complete
rm .lecturebridge/installing
