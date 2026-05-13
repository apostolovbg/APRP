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

  local script_dir root_dir config_file_value config_file env_file
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  root_dir="$(cd "${script_dir}/.." && pwd)"
  env_file="${DEPLOY_ENV_FILE:-}"

  if [[ -z "${env_file}" ]]; then
    env_file=".env.primary"
  fi

  DEPLOY_ENV_FILE="${env_file}"
  config_file_value="${APRP_CONFIG_FILE:-ops/opsconfig.yaml}"
  config_file="$(
    deploy_resolve_repo_path "${root_dir}" "${config_file_value}"
  )"

  if [[ ! -f "${config_file}" ]]; then
    echo "Deploy config is missing: ${config_file}" >&2
    return 1
  fi

  deploy_require_command python3

  eval "$(
    python3 "${script_dir}/opsconfig.py" deploy --config "${config_file}"
  )"

  deploy_require_command git
  deploy_require_command docker

  DEPLOY_ROOT_DIR="${root_dir}"
  DEPLOY_COMMON_INITIALIZED=1
}

deploy_validate_env_file() {
  local env_file="${DEPLOY_ENV_FILE}"
  local env_path="${DEPLOY_ROOT_DIR}/${env_file#./}"

  if [[ ! -f "${env_path}" ]]; then
    echo "Deploy env file is missing: ${env_path}" >&2
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
    -e APRP_APP_NAME="${APRP_APP_NAME}" \
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
