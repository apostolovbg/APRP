#!/usr/bin/env bash
# Galera cold-path helpers: status probes and rebuild steps.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./ops/db_mirror_restore.sh <command>

  cluster-status   Show wsrep status from the local db service (primary stack).
  mirror-status    Show wsrep status from db-mirror (set COMPOSE_FILE=compose.
                   mirror.yaml on the mirror host; APRP_DB_SERVICE=db-mirror).
  mirror-restore   Print the mirror restore procedure (no host changes).
  mirror-reseed    Print the mirror reseed procedure (no host changes).
  mirror-rejoin    Print the mirror rejoin procedure (no host changes).
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

print_mirror_restore() {
  cat <<'EOF'
Restore mirror from a backup session
------------------------------------
1) Restore the database/session bundle with `./ops/backup.sh restore`.
2) Start the mirror stack with `./ops/deploy_mirror.sh`.
3) Verify `./ops/db_mirror_restore.sh mirror-status` reports wsrep ready.
EOF
}

print_mirror_reseed() {
  cat <<'EOF'
Reseed mirror from the primary source of truth
---------------------------------------------
1) Stop the mirror stack with `docker compose -f compose.mirror.yaml down`.
2) Remove the mirror volume with `docker compose -f compose.mirror.yaml down
   -v` if the datadir must be rebuilt from scratch.
3) Relaunch the mirror stack with `./ops/deploy_mirror.sh`.
4) Verify `./ops/db_mirror_restore.sh mirror-status` reports wsrep ready.
EOF
}

print_mirror_rejoin() {
  cat <<'EOF'
Rejoin mirror after a reseed or restore
--------------------------------------
1) Restart the mirror stack with `./ops/deploy_mirror.sh`.
2) Wait for `./ops/db_mirror_restore.sh mirror-status` to report ready.
3) If the primary host needs a rebuild, restore site files separately with
   `./ops/backup.sh restore` before bringing ERP services back up.
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
  mirror-restore)
    print_mirror_restore
    ;;
  mirror-reseed)
    print_mirror_reseed
    ;;
  mirror-rejoin)
    print_mirror_rejoin
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
