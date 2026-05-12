#!/usr/bin/env bash
set -euo pipefail

# Canonical APRP site setup helper.
# CI, deploy, and bench rebuilds call this before migration.

site_setup_require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    return 1
  fi
}

site_setup_append_app() {
  local apps_txt="$1"
  local desired_app="$2"

  if grep -qx "${desired_app}" "${apps_txt}" 2>/dev/null; then
    return 0
  fi

  if [[ -s "${apps_txt}" ]]; then
    local last_char
    last_char="$(tail -c1 "${apps_txt}" 2>/dev/null || true)"
    if [[ "${last_char}" != $'\n' ]]; then
      printf '\n' >> "${apps_txt}"
    fi
  fi

  printf '%s\n' "${desired_app}" >> "${apps_txt}"
}

site_setup_install_app_with_retry() {
  local site_name="$1"
  local desired_app="$2"
  local attempts="${SITE_SETUP_INSTALL_RETRIES:-5}"
  local n=0

  while [[ "${n}" -lt "${attempts}" ]]; do
    if bench --site "${site_name}" install-app "${desired_app}"; then
      return 0
    fi
    n=$((n + 1))
    if [[ "${n}" -lt "${attempts}" ]]; then
      echo "site_setup: install-app ${desired_app} failed" >&2
      echo "attempt ${n}/${attempts}; retrying..." >&2
      sleep 20
    fi
  done

  echo "site_setup: install-app ${desired_app} failed" >&2
  echo "after ${attempts} attempts" >&2
  return 1
}

site_setup_recreate_site() {
  local site_root="$1"
  local site_name="$2"
  local bootstrap_db_host="$3"
  local bootstrap_db_port="$4"
  local db_root_password="$5"
  local admin_password="$6"

  rm -rf "${site_root}"
  bench new-site "${site_name}" \
    --db-host "${bootstrap_db_host}" \
    --db-port "${bootstrap_db_port}" \
    --db-root-password "${db_root_password}" \
    --admin-password "${admin_password}" \
    --mariadb-user-host-login-scope=%
}

site_setup_main() {
  local bench_root="${BENCH_ROOT:-/home/frappe/frappe-bench}"
  local site_name="${SITE_NAME:-kuche.aprp.store}"
  local app_name="${APRP_APP_NAME:-aprp}"
  local db_host="${DB_HOST:-proxysql}"
  local db_port="${DB_PORT:-6033}"
  local bootstrap_db_host="${BOOTSTRAP_DB_HOST:-db}"
  local bootstrap_db_port="${BOOTSTRAP_DB_PORT:-3306}"
  : "${DB_ROOT_PASSWORD:?DB_ROOT_PASSWORD is required}"
  : "${ADMIN_PASSWORD:?ADMIN_PASSWORD is required}"
  local db_root_password="${DB_ROOT_PASSWORD}"
  local admin_password="${ADMIN_PASSWORD}"
  local redis_cache="${REDIS_CACHE:-redis://redis-cache:6379}"
  local redis_queue="${REDIS_QUEUE:-redis://redis-queue:6379}"
  local redis_socketio="${REDIS_SOCKETIO:-redis://redis-socketio:6379}"
  local site_root="${bench_root}/sites/${site_name}"
  local apps_txt="${bench_root}/sites/apps.txt"
  local installed_apps

  export PATH="${bench_root}/env/bin:${PATH}"
  site_setup_require_command bench
  cd "${bench_root}"

  bench set-config -g db_host "${db_host}"
  bench set-config -g db_port "${db_port}"
  bench set-config -g redis_cache "${redis_cache}"
  bench set-config -g redis_queue "${redis_queue}"
  bench set-config -g redis_socketio "${redis_socketio}"

  if [[ ! -f "${site_root}/site_config.json" ]]; then
    bench new-site "${site_name}" \
      --db-host "${bootstrap_db_host}" \
      --db-port "${bootstrap_db_port}" \
      --db-root-password "${db_root_password}" \
      --admin-password "${admin_password}" \
      --mariadb-user-host-login-scope=%
  fi

  if ! bench --site "${site_name}" set-config db_host "${db_host}"; then
    echo "site_setup: failed to update db_host; recreating site directory" >&2
    site_setup_recreate_site \
      "${site_root}" \
      "${site_name}" \
      "${bootstrap_db_host}" \
      "${bootstrap_db_port}" \
      "${db_root_password}" \
      "${admin_password}"
    bench --site "${site_name}" set-config db_host "${db_host}"
  fi
  bench --site "${site_name}" set-config db_port "${db_port}"

  mkdir -p "$(dirname "${apps_txt}")"
  touch "${apps_txt}"
  site_setup_append_app "${apps_txt}" erpnext
  site_setup_append_app "${apps_txt}" "${app_name}"

  if ! installed_apps="$(bench --site "${site_name}" list-apps)"; then
    echo "site_setup: site metadata is corrupted;" >&2
    echo "recreating site directory" >&2
    site_setup_recreate_site \
      "${site_root}" \
      "${site_name}" \
      "${bootstrap_db_host}" \
      "${bootstrap_db_port}" \
      "${db_root_password}" \
      "${admin_password}"
    bench --site "${site_name}" set-config db_host "${db_host}"
    bench --site "${site_name}" set-config db_port "${db_port}"
    installed_apps="$(bench --site "${site_name}" list-apps)"
  fi

  for desired_app in erpnext "${app_name}"; do
    if ! printf "%s\n" "${installed_apps}" | grep -qx "${desired_app}"; then
      site_setup_install_app_with_retry "${site_name}" "${desired_app}"
      installed_apps="$(bench --site "${site_name}" list-apps)"
    fi
  done
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  site_setup_main "$@"
fi
