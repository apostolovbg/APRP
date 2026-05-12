#!/usr/bin/env bash
# Galera cold-path helpers: status probes and rebuild steps.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./ops/db_mirror_restore.sh <command>

  cluster-status   Show wsrep status from the local db service (primary stack).
  mirror-status    Show wsrep status from db-mirror (set COMPOSE_FILE=compose.
                   mirror.yaml on the mirror host; APRP_DB_SERVICE=db-mirror).
  print-rebuild    Print the manual rebuild procedure (no host changes).
  wipe-primary     DANGER: document only — prints steps; set
                   APRP_CONFIRM_DATADIR_WIPE=1 to print wipe commands.
EOF
}

req_compose() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker is not on PATH" >&2
    exit 1
  fi
}

run_sql_status() {
  local comp="${COMPOSE_FILE:-compose.yaml}"
  local svc="${APRP_DB_SERVICE:-db}"
  req_compose
  docker compose -f "${comp}" exec -T "${svc}" \
    sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mariadb -uroot -e \
      "SHOW GLOBAL STATUS WHERE Variable_name LIKE '\''wsrep_%'\''"'
}

print_rebuild() {
  cat <<'EOF'
Rebuild primary from surviving mirror (operator procedure)
----------------------------------------------------------
1) Stop ERP writers: on the primary host, `docker compose stop backend` (and
   queue/websocket/scheduler as needed) so no writes race recovery.
2) Confirm mirror host `db-mirror` is SYNCED (run `./ops/db_mirror_restore.sh
   mirror-status` there with COMPOSE_FILE=compose.mirror.yaml).
3) Snapshot policy: prefer SST/Galera donor/joiner flows.
4) When mysqld is healthy, `./ops/deploy.sh` then verify ProxySQL and ERP.

Always reconcile site files with `./ops/backup.sh restore` when restoring rows
alone is insufficient.
EOF
}

wipe_primary_docs() {
  if [[ "${APRP_CONFIRM_DATADIR_WIPE:-}" != "1" ]]; then
    cat <<'EOF'
Refusing wipe hints until APRP_CONFIRM_DATADIR_WIPE=1 is set in the
environment.
EOF
    exit 1
  fi
  cat <<'EOF'
Example destructive sequence (YOU MUST ADAPT PATHS AND BACKUPS):
  docker compose stop db backend
  docker volume rm <project>_db-data   # CAUSES DATA LOSS — backup first
  docker compose up -d db
EOF
}

cmd="${1:-}"
case "${cmd}" in
  cluster-status)
    req_compose
    run_sql_status
    ;;
  mirror-status)
    export COMPOSE_FILE="${COMPOSE_FILE:-compose.mirror.yaml}"
    export APRP_DB_SERVICE="${APRP_DB_SERVICE:-db-mirror}"
    run_sql_status
    ;;
  print-rebuild)
    print_rebuild
    ;;
  wipe-primary)
    wipe_primary_docs
    ;;
  ""|-h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac
