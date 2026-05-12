#!/usr/bin/env bash
set -euo pipefail

# Canonical repo-owned deploy command for the APRP primary host.
# GitHub-hosted workflow signals this host over SSH and runs it locally.
# It syncs the host checkout, restarts the Compose services, prepares the
# APRP site, runs migrations inside the backend container, prepares the shared
# backup volume, and then triggers a post-deploy backup from the same runtime.

deploy_resolve_repo_path() {
  local root_dir="$1"
  local candidate="$2"

  if [[ -z "${candidate}" ]]; then
    return 0
  fi

  if [[ "${candidate}" == /* ]]; then
    printf '%s\n' "${candidate}"
    return 0
  fi

  printf '%s\n' "${root_dir}/${candidate#./}"
}

deploy_require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    return 1
  fi
}

deploy_init() {
  if [[ "${DEPLOY_COMMON_INITIALIZED:-}" == "1" ]]; then
    return 0
  fi

  local script_dir root_dir config_file_value config_file config_json env_file
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  root_dir="$(cd "${script_dir}/.." && pwd)"
  env_file="${DEPLOY_ENV_FILE:-}"

  if [[ -z "${env_file}" ]]; then
    env_file=".env.primary"
  fi

  DEPLOY_ENV_FILE="${env_file}"
  config_file_value="${DEPLOY_CONFIG_FILE:-ops/deploy_config.json}"
  config_file="$(
    deploy_resolve_repo_path "${root_dir}" "${config_file_value}"
  )"

  if [[ ! -f "${config_file}" ]]; then
    echo "Deploy config is missing: ${config_file}" >&2
    return 1
  fi

  deploy_require_command python3

  config_json="$(
    python3 - "${config_file}" <<'PY'
import json
import os
import shlex
import sys

config_path = sys.argv[1]
data = json.loads(open(config_path, encoding="utf-8").read())

site = data.get("site", {})
git = data.get("git", {})
compose = data.get("compose", {})

def expand(value: object, default: str | None = None) -> str | None:
    token = default if value is None else str(value)
    if token is None:
        return None
    return os.path.expandvars(os.path.expanduser(token))

def emit(name: str, value: object) -> None:
    if value is None:
        return
    print(f"{name}={shlex.quote(str(value))}")

emit("DEPLOY_SITE_NAME", site.get("name", "kuche.aprp.store"))
emit("DEPLOY_GIT_REMOTE", git.get("remote", "origin"))
emit("DEPLOY_GIT_BRANCH", git.get("branch", "main"))
emit(
    "DEPLOY_GIT_SYNC_REMOTE",
    "1" if git.get("sync_remote", False) else "0",
)
emit("DEPLOY_COMPOSE_FILE", expand(compose.get("file"), "compose.yaml"))
emit(
    "DEPLOY_BUILD_SERVICES",
    " ".join(compose.get("build_services", ["caddy"])),
)
emit(
    "DEPLOY_RESTART_SERVICES",
    " ".join(
        compose.get(
            "restart_services",
            [
                "backend",
                "websocket",
                "queue-default",
                "queue-short",
                "queue-long",
                "scheduler",
            ],
        )
    ),
)
PY
  )"
  eval "${config_json}"

  deploy_require_command git
  deploy_require_command docker

  DEPLOY_ROOT_DIR="${root_dir}"
  DEPLOY_COMMON_INITIALIZED=1
}

deploy_require_env_var() {
  local file_path="$1"
  local key="$2"

  python3 - "${file_path}" "${key}" <<'PY'
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

deploy_validate_env_file() {
  local env_file="${DEPLOY_ENV_FILE}"
  local env_path="${DEPLOY_ROOT_DIR}/${env_file#./}"
  local cluster_members

  if [[ ! -f "${env_path}" ]]; then
    echo "Deploy env file is missing: ${env_path}" >&2
    return 1
  fi

  cluster_members="$(
    deploy_require_env_var "${env_path}" "APRP_GALERA_CLUSTER_MEMBERS"
  )"
  if [[ "${cluster_members}" != *"kuche.aprp.store"* ]] \
    || [[ "${cluster_members}" != *"kotka.aprp.store"* ]]; then
    echo "Primary deploy refused: ${env_file}" >&2
    echo "APRP_GALERA_CLUSTER_MEMBERS must include" >&2
    echo "kuche.aprp.store and kotka.aprp.store" >&2
    return 1
  fi
}

deploy_pull_target_commit() {
  git -C "${DEPLOY_ROOT_DIR}" switch "${DEPLOY_GIT_BRANCH}"
  if [[ "${DEPLOY_GIT_SYNC_REMOTE}" != "1" ]]; then
    return 0
  fi

  git -C "${DEPLOY_ROOT_DIR}" fetch --prune \
    "${DEPLOY_GIT_REMOTE}" "${DEPLOY_GIT_BRANCH}"
  git -C "${DEPLOY_ROOT_DIR}" pull --ff-only \
    "${DEPLOY_GIT_REMOTE}" "${DEPLOY_GIT_BRANCH}"
}

deploy_emit_stack_diagnostics() {
  echo "Deploy diagnostics (compose reload failed):" >&2
  cd "${DEPLOY_ROOT_DIR}" || return 0
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f "${DEPLOY_COMPOSE_FILE}" \
    ps -a >&2 || true
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f "${DEPLOY_COMPOSE_FILE}" \
    logs --tail 200 db >&2 || true
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f "${DEPLOY_COMPOSE_FILE}" \
    logs --tail 120 garbd >&2 || true
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f "${DEPLOY_COMPOSE_FILE}" \
    logs --tail 80 proxysql >&2 || true
}

deploy_reload_stack() {
  local -a build_services restart_services

  read -r -a build_services <<<"${DEPLOY_BUILD_SERVICES}"
  read -r -a restart_services <<<"${DEPLOY_RESTART_SERVICES}"

  cd "${DEPLOY_ROOT_DIR}"
  export APRP_COMPOSE_ENV_FILE="${DEPLOY_ENV_FILE}"

  if ((${#build_services[@]})); then
    if ! docker compose --env-file "${DEPLOY_ENV_FILE}" -f \
      "${DEPLOY_COMPOSE_FILE}" up -d --build \
      "${build_services[@]}"
    then
      deploy_emit_stack_diagnostics
      return 1
    fi
  fi

  if ((${#restart_services[@]})); then
    if ! docker compose --env-file "${DEPLOY_ENV_FILE}" -f \
      "${DEPLOY_COMPOSE_FILE}" restart \
      "${restart_services[@]}"
    then
      deploy_emit_stack_diagnostics
      return 1
    fi
  fi
}

deploy_prepare_site() {
  cd "${DEPLOY_ROOT_DIR}"
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f \
    "${DEPLOY_COMPOSE_FILE}" exec -u frappe -T \
    -e SITE_NAME="${DEPLOY_SITE_NAME}" \
    -e APRP_APP_NAME=aprp \
    backend bash -lc '
    set -euo pipefail
    export PATH=/home/frappe/frappe-bench/env/bin:$PATH
    cd /home/frappe/frappe-bench/apps/aprp
    bash ./ops/site_setup.sh
  '
}

deploy_run_migrations() {
  cd "${DEPLOY_ROOT_DIR}"
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f \
    "${DEPLOY_COMPOSE_FILE}" exec -T backend \
    bench --site "${DEPLOY_SITE_NAME}" migrate
}

deploy_prepare_backup_volume() {
  cd "${DEPLOY_ROOT_DIR}"
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f \
    "${DEPLOY_COMPOSE_FILE}" exec -u root -T backend sh -lc '
    mkdir -p /backups/aprp
    chown -R frappe:frappe /backups
  '
}

deploy_run_post_deploy_backup() {
  cd "${DEPLOY_ROOT_DIR}"
  docker compose --env-file "${DEPLOY_ENV_FILE}" -f \
    "${DEPLOY_COMPOSE_FILE}" exec -u frappe -T backend bash -lc '
    export PATH=/home/frappe/frappe-bench/env/bin:$PATH
    cd /home/frappe/frappe-bench/apps/aprp
    bash ./ops/backup.sh backup
  '
}

deploy_main() {
  deploy_init
  deploy_validate_env_file
  deploy_pull_target_commit
  deploy_reload_stack
  deploy_prepare_site
  deploy_run_migrations
  deploy_prepare_backup_volume
  deploy_run_post_deploy_backup
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  deploy_main "$@"
fi
