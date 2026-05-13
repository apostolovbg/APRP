#!/usr/bin/env bash
set -euo pipefail

# Deploy entrypoint for the APRP database mirror host.
#
# Expected layout:
# - This repository is checked out on the mirror machine at the same canonical
#   path as the primary host.
# - The mirror machine maintains its own `.env.mirror` file (never committed).
# - The mirror uses `compose.mirror.yaml`, its own volume, and its own
#   Compose network. It does not run ERP services.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "${repo_root}"

env_file="${APRP_COMPOSE_ENV_FILE:-.env.mirror}"
config_file_value="${APRP_CONFIG_FILE:-ops/opsconfig.yaml}"
config_file="$(python3 - "$repo_root" "$config_file_value" <<'PY'
import os
import sys

root_dir = sys.argv[1]
candidate = sys.argv[2]
if os.path.isabs(candidate):
    print(candidate)
else:
    print(os.path.join(root_dir, candidate))
PY
)"

if [[ ! -f "${env_file}" ]]; then
  echo "Mirror env file is missing: ${env_file}" >&2
  exit 1
fi

if [[ ! -f "${config_file}" ]]; then
  echo "Mirror config is missing: ${config_file}" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not on PATH" >&2
  exit 1
fi

eval "$(
  python3 "${script_dir}/opsconfig.py" mirror --config "${config_file}"
)"

if command -v git >/dev/null 2>&1; then
  git fetch --quiet origin
  git pull --ff-only
fi

docker compose --env-file "${env_file}" -f compose.mirror.yaml up -d \
  --remove-orphans
