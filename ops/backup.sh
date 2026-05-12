#!/usr/bin/env bash
set -euo pipefail

# Canonical APRP backup entrypoint.
# Runs inside the backend service from compose.yaml.

backup_resolve_repo_path() {
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

backup_require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    return 1
  fi
}

backup_init() {
  if [[ "${BACKUP_COMMON_INITIALIZED:-}" == "1" ]]; then
    return 0
  fi

  local script_dir root_dir config_file_value config_file config_json
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  root_dir="$(cd "${script_dir}/.." && pwd)"
  config_file_value="${BACKUP_CONFIG_FILE:-ops/backup_config.json}"
  config_file="$(
    backup_resolve_repo_path "${root_dir}" "${config_file_value}"
  )"

  if [[ ! -f "${config_file}" ]]; then
    echo "Backup config is missing: ${config_file}" >&2
    return 1
  fi

  backup_require_command python3

  config_json="$(
    python3 - "${config_file}" <<'PY'
import json
import os
import shlex
import sys

config_path = sys.argv[1]
data = json.loads(open(config_path, encoding="utf-8").read())

site = data.get("site", {})
retention = data.get("retention", {})
offsite = data.get("offsite", {})

def expand(value: object, default: str | None = None) -> str | None:
    token = default if value is None else str(value)
    if token is None:
        return None
    return os.path.expandvars(os.path.expanduser(token))

def emit(name: str, value: object) -> None:
    if value is None:
        return
    print(f"{name}={shlex.quote(str(value))}")

emit("BACKUP_SITE_NAME", site.get("name", "kuche.aprp.store"))
emit(
    "BACKUP_LOCAL_BACKUP_DIR",
    expand(site.get("local_backup_dir"), "/backups/aprp"),
)
emit(
    "BACKUP_BENCH_SITES_ROOT",
    expand(
        site.get("bench_sites_root"),
        "/home/frappe/frappe-bench/sites",
    ),
)
emit("BACKUP_TZ", data.get("timezone", "UTC"))
emit("BACKUP_KEEP_DAILY", retention.get("keep_daily", 7))
emit("BACKUP_RCLONE_REMOTE", offsite.get("remote", ""))
emit(
    "BACKUP_RCLONE_CONF",
    expand(offsite.get("rclone_conf"), "ops/rclone.conf"),
)
emit("BACKUP_B2_BUCKET", offsite.get("bucket", ""))
emit("BACKUP_B2_PREFIX", offsite.get("prefix", "aprp"))
emit("BACKUP_B2_CAP_BYTES", offsite.get("cap_bytes", 10737418240))
emit("BACKUP_B2_TARGET_PERCENT", offsite.get("target_percent", 90))
emit("BACKUP_B2_TARGET_BYTES", offsite.get("target_bytes"))
PY
  )"
  eval "${config_json}"

  backup_require_command bench
  backup_require_command git
  backup_require_command rclone
  backup_prepare_backup_volume

  BACKUP_ROOT_DIR="${root_dir}"
  BACKUP_SITE_SLUG="${BACKUP_SITE_NAME//./_}"
  BACKUP_SITE_ROOT="${BACKUP_LOCAL_BACKUP_DIR}/${BACKUP_SITE_NAME}"
  BACKUP_LATEST_LINK="${BACKUP_SITE_ROOT}/latest"
  BACKUP_RCLONE_CONF="$(backup_resolve_repo_path "${root_dir}" \
    "${BACKUP_RCLONE_CONF}")"

  BACKUP_COMMON_INITIALIZED=1
}

backup_prepare_backup_volume() {
  mkdir -p /backups/aprp
  if [[ "$(id -u)" -eq 0 ]]; then
    chown -R frappe:frappe /backups
  fi
}

backup_utc_date() {
  TZ="${BACKUP_TZ}" date +"%Y-%m-%d"
}

backup_utc_time() {
  TZ="${BACKUP_TZ}" date +"%H%M%S"
}

backup_utc_stamp() {
  TZ="${BACKUP_TZ}" date +"%Y-%m-%dT%H%M%SZ"
}

backup_session_dir() {
  local backup_date="$1"
  local backup_time="$2"

  printf '%s/%s/%s' \
    "${BACKUP_SITE_ROOT}" \
    "${backup_date}" \
    "${backup_time}"
}

backup_latest_session_dir() {
  if [[ -L "${BACKUP_LATEST_LINK}" || -d "${BACKUP_LATEST_LINK}" ]]; then
    local resolved
    resolved="$(backup_resolve_dir_link "${BACKUP_LATEST_LINK}")"
    if [[ -n "${resolved}" ]]; then
      printf '%s\n' "${resolved}"
      return 0
    fi
  fi

  if [[ -d "${BACKUP_SITE_ROOT}" ]]; then
    find "${BACKUP_SITE_ROOT}" -mindepth 2 -maxdepth 2 -type d \
      | LC_ALL=C sort \
      | tail -n 1
  fi
}

backup_capture_metadata() {
  local session_dir="$1"

  hostname > "${session_dir}/container-hostname.txt"
  whoami > "${session_dir}/container-user.txt"
  id > "${session_dir}/container-id.txt"
  pwd > "${session_dir}/container-working-directory.txt"
  bench --version > "${session_dir}/bench-version.txt"
  git -C "${BACKUP_ROOT_DIR}" rev-parse --short HEAD \
    > "${session_dir}/git-commit.txt"
  git -C "${BACKUP_ROOT_DIR}" rev-parse --abbrev-ref HEAD \
    > "${session_dir}/git-branch.txt"
  git -C "${BACKUP_ROOT_DIR}" status --short > "${session_dir}/git-status.txt"
}

backup_write_manifest() {
  local session_dir="$1"
  local backup_stamp="$2"
  local db_file="$3"
  local public_file="$4"
  local private_file="$5"
  local site_config_file="$6"
  local common_site_config_file="$7"
  local offsite_target="disabled"

  if [[ -n "${BACKUP_RCLONE_REMOTE}" && -n "${BACKUP_B2_BUCKET}" ]]; then
    offsite_target="${BACKUP_RCLONE_REMOTE}:${BACKUP_B2_BUCKET}/\
${BACKUP_B2_PREFIX}"
  fi

  cat > "${session_dir}/manifest.txt" <<EOF
Backup session: ${backup_stamp} ${BACKUP_TZ}
APRP site: ${BACKUP_SITE_NAME}
Repo commit: $(cat "${session_dir}/git-commit.txt")
Repo branch: $(cat "${session_dir}/git-branch.txt")
Local backup root: ${BACKUP_LOCAL_BACKUP_DIR}
APRP site backup root: ${BACKUP_SITE_ROOT}
Offsite target: ${offsite_target}
Artifacts:
- ${db_file}
- ${public_file}
- ${private_file}
- ${site_config_file}
- ${common_site_config_file}
- ${session_dir}/container-hostname.txt
- ${session_dir}/container-user.txt
- ${session_dir}/container-id.txt
- ${session_dir}/container-working-directory.txt
- ${session_dir}/bench-version.txt
- ${session_dir}/git-commit.txt
- ${session_dir}/git-branch.txt
- ${session_dir}/git-status.txt
Restore:
- Restore this session with \`./ops/backup.sh restore\` inside the
  backend service.
- Restore common_site_config.json and site_config.json before rejoining
  the APRP site.
- Restore repo-owned runtime files from Git, not from this ERP-state backup.
EOF
}

backup_update_latest_pointer() {
  local session_dir="$1"
  local backup_date="$2"

  mkdir -p "${BACKUP_SITE_ROOT}/${backup_date}"
  ln -sfn "${session_dir}" "${BACKUP_LATEST_LINK}"
}

backup_resolve_dir_link() {
  local link="$1"

  (cd "${link}" 2>/dev/null && pwd -P) || true
}

backup_capture_local_session() {
  local backup_date backup_time backup_stamp
  local session_dir db_file public_file private_file
  local site_config_file common_site_config_file

  backup_date="$(backup_utc_date)"
  backup_time="$(backup_utc_time)"
  backup_stamp="${backup_date}T${backup_time}Z"
  session_dir="$(backup_session_dir "${backup_date}" "${backup_time}")"
  db_file="${session_dir}/${BACKUP_SITE_SLUG}-${backup_stamp}-database.sql.gz"
  public_file="${session_dir}/${BACKUP_SITE_SLUG}-${backup_stamp}-files.tar"
  private_file="${session_dir}/${BACKUP_SITE_SLUG}-\
${backup_stamp}-private-files.tar"
  site_config_file="${session_dir}/site_config.json"
  common_site_config_file="${session_dir}/common_site_config.json"

  mkdir -p "${session_dir}"

  bench --site "${BACKUP_SITE_NAME}" backup \
    --with-files \
    --backup-path-db "${db_file}" \
    --backup-path-files "${public_file}" \
    --backup-path-private-files "${private_file}" \
    --backup-path-conf "${site_config_file}" >&2

  cp "${BACKUP_BENCH_SITES_ROOT}/common_site_config.json" \
    "${common_site_config_file}"

  if [[ ! -f "${db_file}" || ! -f "${public_file}" \
    || ! -f "${private_file}" ]]; then
    echo "Bench backup did not write the expected session artifacts." >&2
    return 1
  fi

  if [[ ! -f "${site_config_file}" \
    || ! -f "${common_site_config_file}" ]]; then
    echo "Backup config files are missing from the session bundle." >&2
    return 1
  fi

  backup_capture_metadata "${session_dir}"
  backup_write_manifest \
    "${session_dir}" \
    "${backup_stamp}" \
    "${db_file}" \
    "${public_file}" \
    "${private_file}" \
    "${site_config_file}" \
    "${common_site_config_file}"
  backup_update_latest_pointer "${session_dir}" "${backup_date}"

  printf '%s\n' "${session_dir}"
}

backup_stage_remote_restore_source() {
  local source_path="$1"
  local staging_root staging_dir

  staging_root="$(mktemp -d /tmp/aprp-restore-XXXXXX)"
  staging_dir="${staging_root}/session"
  mkdir -p "${staging_dir}"

  rclone --config "${BACKUP_RCLONE_CONF}" copy \
    "${source_path%/}" \
    "${staging_dir}" \
    --fast-list

  printf '%s\n' "${staging_dir}"
}

backup_resolve_restore_source() {
  local restore_input="${1:-}"

  if [[ -z "${restore_input}" ]]; then
    if [[ -d "${BACKUP_LATEST_LINK}" || -L "${BACKUP_LATEST_LINK}" ]]; then
      restore_input="$(backup_resolve_dir_link "${BACKUP_LATEST_LINK}")"
    fi
  fi

  if [[ -z "${restore_input}" ]]; then
    restore_input="$(backup_latest_session_dir || true)"
  fi

  if [[ -z "${restore_input}" ]]; then
    echo "No backup session found to restore." >&2
    return 1
  fi

  if [[ "${restore_input}" == *:* ]]; then
    backup_stage_remote_restore_source "${restore_input}"
    return 0
  fi

  if [[ -d "${restore_input}" ]]; then
    (cd "${restore_input}" && pwd -P)
    return 0
  fi

  if [[ -f "${restore_input}" ]]; then
    (cd "$(dirname "${restore_input}")" && pwd -P)
    return 0
  fi

  echo "Restore source not found: ${restore_input}" >&2
  return 1
}

backup_find_latest_match() {
  local search_root="$1"
  shift

  find "${search_root}" -maxdepth 1 -type f \( "$@" \) \
    | LC_ALL=C sort \
    | tail -n 1
}

backup_find_latest_public_file() {
  local search_root="$1"

  find "${search_root}" -maxdepth 1 -type f \
    \( -name '*-files.tar' -o -name '*-files.tgz' \
    -o -name '*-files.tar.gz' \) \
    ! -name '*private-files*' \
    | LC_ALL=C sort \
    | tail -n 1
}

backup_sync_session_to_offsite() {
  local session_arg="${1:-}"
  local session_dir backup_date backup_time remote_session_path

  if [[ -n "${session_arg}" ]]; then
    if [[ -d "${session_arg}" ]]; then
      session_dir="$(cd "${session_arg}" && pwd -P)"
    else
      session_dir="$(cd "$(dirname "${session_arg}")" && pwd -P)"
    fi
  else
    session_dir="$(backup_latest_session_dir || true)"
  fi

  if [[ -z "${session_dir}" || ! -d "${session_dir}" ]]; then
    echo "No backup session found to sync." >&2
    return 1
  fi

  if [[ -z "${BACKUP_RCLONE_REMOTE}" || -z "${BACKUP_B2_BUCKET}" ]]; then
    echo "B2 backup settings are missing from ops/backup_config.json." >&2
    return 1
  fi

  backup_date="$(basename "$(dirname "${session_dir}")")"
  backup_time="$(basename "${session_dir}")"
  remote_session_path="$(
    backup_remote_session_path "${backup_date}" "${backup_time}"
  )"

  rclone --config "${BACKUP_RCLONE_CONF}" copy \
    "${session_dir}" \
    "${remote_session_path}" \
    --fast-list
  date -u +"%Y-%m-%dT%H:%M:%SZ" > "${session_dir}/offsite_sync_ok.stamp"

  printf 'Offsite sync complete: %s -> %s\n' \
    "${session_dir}" \
    "${remote_session_path}"
}

backup_remote_root() {
  printf '%s:%s/%s' \
    "${BACKUP_RCLONE_REMOTE}" \
    "${BACKUP_B2_BUCKET}" \
    "${BACKUP_B2_PREFIX}"
}

backup_remote_session_root() {
  printf '%s' "$(backup_remote_root)"
}

backup_remote_session_path() {
  local backup_date="$1"
  local backup_time="$2"

  printf '%s/%s/%s' \
    "$(backup_remote_session_root)" \
    "${backup_date}" \
    "${backup_time}"
}

backup_restore_session() {
  local restore_input="${1:-}"
  local restore_dir sql_file public_file private_file
  local site_config_file common_site_config_file cleanup_root
  local restore_args=()

  backup_init

  cleanup_root=""
  restore_dir="$(backup_resolve_restore_source "${restore_input}")"
  if [[ "${restore_dir}" == /tmp/aprp-restore-* ]]; then
    cleanup_root="$(dirname "${restore_dir}")"
    trap 'rm -rf "${cleanup_root}"' RETURN
  fi

  sql_file="$(backup_find_latest_match "${restore_dir}" \
    -name '*database*.sql.gz' -o -name '*.sql.gz')"
  public_file="$(backup_find_latest_public_file "${restore_dir}")"
  private_file="$(backup_find_latest_match "${restore_dir}" \
    -name '*private-files.tar' -o -name '*private-files.tgz' \
    -o -name '*private-files.tar.gz' || true)"
  site_config_file="$(backup_find_latest_match "${restore_dir}" \
    -name 'site_config.json' -o -name '*site-config*.json' || true)"
  common_site_config_file="$(backup_find_latest_match "${restore_dir}" \
    -name 'common_site_config.json' || true)"

  if [[ -z "${sql_file}" || ! -f "${sql_file}" ]]; then
    echo "Database backup not found in restore source: ${restore_dir}" >&2
    return 1
  fi

  if [[ -z "${public_file}" || ! -f "${public_file}" ]]; then
    echo "Public files backup not found in restore source: ${restore_dir}" >&2
    return 1
  fi

  if [[ -z "${private_file}" || ! -f "${private_file}" ]]; then
    echo "Private files backup not found in restore source: ${restore_dir}" >&2
    return 1
  fi

  if [[ -z "${site_config_file}" || ! -f "${site_config_file}" ]]; then
    echo "Site config backup not found in restore source: ${restore_dir}" >&2
    return 1
  fi

  if [[ -z "${common_site_config_file}" \
    || ! -f "${common_site_config_file}" ]]; then
    echo "Common site config backup not found in restore source:" >&2
    echo "${restore_dir}" >&2
    return 1
  fi

  mkdir -p "${BACKUP_BENCH_SITES_ROOT}/${BACKUP_SITE_NAME}"

  restore_args=(
    --force
    --with-public-files "${public_file}"
    --with-private-files "${private_file}"
  )

  bench --site "${BACKUP_SITE_NAME}" restore "${restore_args[@]}" "${sql_file}"

  cp "${site_config_file}" \
    "${BACKUP_BENCH_SITES_ROOT}/${BACKUP_SITE_NAME}/site_config.json"
  cp "${common_site_config_file}" \
    "${BACKUP_BENCH_SITES_ROOT}/common_site_config.json"

  bench --site "${BACKUP_SITE_NAME}" migrate

  printf 'Restore complete: %s -> %s\n' "${restore_dir}" "${BACKUP_SITE_NAME}"
}

backup_run_backup() {
  local session_dir

  backup_init
  cd "${BACKUP_ROOT_DIR}"

  session_dir="$(backup_capture_local_session)"
  if [[ -n "${BACKUP_RCLONE_REMOTE}" && -n "${BACKUP_B2_BUCKET}" ]]; then
    backup_sync_session_to_offsite "${session_dir}"
  fi

  printf 'Backup complete: %s\n' "${session_dir}"
}

backup_usage() {
  cat <<'EOF'
Usage:
  ./ops/backup.sh
  ./ops/backup.sh backup
  ./ops/backup.sh restore [SESSION_DIR|SQL_FILE|REMOTE_SESSION]
  ./ops/backup.sh offsite-sync [SESSION_DIR]
EOF
}

backup_main() {
  local command="${1:-backup}"
  shift || true

  case "${command}" in
    backup)
      backup_run_backup
      ;;
    restore)
      backup_restore_session "${1:-}"
      ;;
    offsite-sync)
      backup_sync_session_to_offsite "${1:-}"
      ;;
    help|-h|--help)
      backup_usage
      ;;
    *)
      echo "Unknown backup command: ${command}" >&2
      backup_usage >&2
      return 1
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  backup_main "$@"
fi
