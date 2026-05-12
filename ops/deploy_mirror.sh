#!/usr/bin/env bash
set -euo pipefail

# Deploy entrypoint for the APRP database mirror host.
#
# Expected layout:
# - This repository is checked out on the mirror machine at the same canonical
#   path as the primary host.
# - The mirror machine maintains its own `.env.mirror` file (never committed).
# - The mirror uses `compose.mirror.yaml` and does not run ERP services.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${repo_root}"

env_file="${APRP_COMPOSE_ENV_FILE:-.env.mirror}"

require_env_var() {
  local file_path="$1"
  local key="$2"

  python3 - "$file_path" "$key" <<'PY'
import sys

path = sys.argv[1]
key = sys.argv[2]

value = None
with open(path, encoding="utf-8") as handle:
    for raw in handle:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, token = line.split("=", 1)
        if name.strip() == key:
            value = token.strip()
            break

if value is None or value == "":
    print(f"Missing required {key} in {path}", file=sys.stderr)
    raise SystemExit(1)

print(value)
PY
}

if [[ ! -f "${env_file}" ]]; then
  echo "Mirror env file is missing: ${env_file}" >&2
  exit 1
fi

cluster_members="$(require_env_var "${env_file}" "APRP_GALERA_CLUSTER_MEMBERS")"
if [[ "${cluster_members}" != *"kotka.aprp.store"* ]]; then
  echo "Mirror deploy refused: ${env_file} APRP_GALERA_CLUSTER_MEMBERS must include kotka.aprp.store" >&2
  exit 1
fi

if command -v git >/dev/null 2>&1; then
  git fetch --quiet origin
  git pull --ff-only
fi

docker compose --env-file "${env_file}" -f compose.mirror.yaml up -d
