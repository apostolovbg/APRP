#!/usr/bin/env bash
# Start MariaDB 10.11 as a Galera member for APRP.

set -euo pipefail

: "${APRP_GALERA_NODE:?APRP_GALERA_NODE must be db or db-mirror}"
# The official MariaDB image uses MYSQL_* variables. The stack contract uses
# DB_* for app and ops tooling, so map them when present.
if [[ -z "${MYSQL_ROOT_PASSWORD:-}" ]] && [[ -n "${DB_ROOT_PASSWORD:-}" ]]; then
  export MYSQL_ROOT_PASSWORD="${DB_ROOT_PASSWORD}"
fi
if [[ -z "${MYSQL_PASSWORD:-}" ]] && [[ -n "${DB_PASSWORD:-}" ]]; then
  export MYSQL_PASSWORD="${DB_PASSWORD}"
fi
if [[ -z "${MYSQL_USER:-}" ]] && [[ -n "${DB_USER:-}" ]]; then
  export MYSQL_USER="${DB_USER}"
fi

: "${MYSQL_ROOT_PASSWORD:?MYSQL_ROOT_PASSWORD (or DB_ROOT_PASSWORD) is required}"

datadir="/var/lib/mysql"
cluster_name="${APRP_GALERA_CLUSTER_NAME:-aprp_galera}"
cluster_members="${APRP_GALERA_CLUSTER_MEMBERS:-}"
primary_host="${APRP_GALERA_PRIMARY_HOST:-db}"
force_bootstrap="${APRP_GALERA_FORCE_BOOTSTRAP:-0}"
provider="/usr/lib/galera/libgalera_smm.so"

if [[ ! -f "${provider}" ]]; then
  echo "Galera provider missing at ${provider}" >&2
  exit 1
fi

wsrep_ip=""
read -r -a _cand <<<"$(hostname -i)"
for _addr in "${_cand[@]}"; do
  if [[ "${_addr}" != 127.* ]]; then
    wsrep_ip="${_addr}"
    break
  fi
done
if [[ -z "${wsrep_ip}" ]]; then
  wsrep_ip="$(
    ip -4 -o addr show scope global 2>/dev/null |
      awk '{print $4}' |
      cut -d/ -f1 |
      grep -v '^127\.' |
      head -1
  )"
fi
if [[ -z "${wsrep_ip}" ]]; then
  echo "Unable to resolve non-loopback IP for wsrep_node_address." >&2
  exit 1
fi

wait_for_tcp() {
  local host="$1" port="$2" tries="${3:-180}"
  local n=0
  while [[ "${n}" -lt "${tries}" ]]; do
    if timeout 1 bash -c "true &>/dev/tcp/${host}/${port}" 2>/dev/null; then
      return 0
    fi
    n=$((n + 1))
    sleep 1
  done
  return 1
}

wait_for_mysql() {
  local host="$1" tries="${2:-180}"
  local n=0
  while [[ "${n}" -lt "${tries}" ]]; do
    if MYSQL_PWD="${MYSQL_ROOT_PASSWORD}" mariadb -h "${host}" -uroot \
      -e "SELECT 1" &>/dev/null; then
      return 0
    fi
    n=$((n + 1))
    sleep 1
  done
  return 1
}

if [[ "${APRP_GALERA_NODE}" == "db-mirror" ]]; then
  if [[ -z "${cluster_members}" ]]; then
    echo "APRP_GALERA_CLUSTER_MEMBERS is required for db-mirror." >&2
    exit 1
  fi
  wait_for_mysql "${primary_host}" 240
  wait_for_tcp "${primary_host}" "4567" 240
fi

normalize_cluster_members() {
  local raw="$1" self="$2"
  local out=() item

  IFS=',' read -r -a _parts <<<"${raw}"
  for item in "${_parts[@]}"; do
    item="$(printf '%s' "${item}" | xargs)"
    if [[ -z "${item}" ]]; then
      continue
    fi
    if [[ "${item}" == "${self}" ]]; then
      continue
    fi
    out+=("${item}")
  done

  (IFS=','; printf '%s' "${out[*]}")
}

normalized_members="$(normalize_cluster_members "${cluster_members}" "${APRP_GALERA_NODE}")"
wsrep_cluster_address="gcomm://"
if [[ -n "${normalized_members}" ]]; then
  wsrep_cluster_address="gcomm://${normalized_members}"
fi

bootstrap=0
if [[ "${APRP_GALERA_NODE}" == "db" ]]; then
  if [[ ! -d "${datadir}/mysql" ]]; then
    bootstrap=1
    wsrep_cluster_address="gcomm://"
  elif [[ ! -f "${datadir}/grastate.dat" ]]; then
    bootstrap=1
    wsrep_cluster_address="gcomm://"
  fi
fi

if [[ "${APRP_GALERA_NODE}" == "db" ]] && [[ "${force_bootstrap}" == "1" ]]; then
  if [[ -f "${datadir}/grastate.dat" ]] &&
    grep -qE '^safe_to_bootstrap:[[:space:]]*0[[:space:]]*$' \
      "${datadir}/grastate.dat"; then
    echo "Force bootstrap: overriding safe_to_bootstrap to allow recovery" >&2
    sed -i 's/^safe_to_bootstrap:[[:space:]]*0[[:space:]]*$/safe_to_bootstrap: 1/' \
      "${datadir}/grastate.dat"
  fi

  bootstrap=1
  wsrep_cluster_address="gcomm://"
fi

if [[ "${APRP_GALERA_NODE}" == "db" ]] && [[ -z "${normalized_members}" ]]; then
  if [[ -f "${datadir}/grastate.dat" ]] &&
    grep -qE '^safe_to_bootstrap:[[:space:]]*0[[:space:]]*$' \
      "${datadir}/grastate.dat"; then
    echo "Solo Galera: grastate had safe_to_bootstrap:0; allowing this" \
      "single node to form the cluster" >&2
    sed -i 's/^safe_to_bootstrap:[[:space:]]*0[[:space:]]*$/safe_to_bootstrap: 1/' \
      "${datadir}/grastate.dat"
    bootstrap=1
    wsrep_cluster_address="gcomm://"
  fi
fi

cat >/etc/mysql/conf.d/999-aprp-galera-dynamic.cnf <<EOF
[mysqld]
wsrep_on=ON
wsrep_provider=${provider}
wsrep_cluster_name=${cluster_name}
wsrep_node_address=${wsrep_ip}:4567
wsrep_node_name=${APRP_GALERA_NODE}
wsrep_cluster_address=${wsrep_cluster_address}
wsrep_sst_method=mariabackup
wsrep_sst_auth=root:${MYSQL_ROOT_PASSWORD}
EOF

extra=()
if [[ "${bootstrap}" -eq 1 ]]; then
  extra+=(--wsrep-new-cluster)
fi

exec /usr/local/bin/docker-entrypoint.sh mysqld "${extra[@]}"
