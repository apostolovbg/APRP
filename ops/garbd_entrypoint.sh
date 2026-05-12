#!/usr/bin/env bash
# Start Galera Arbitrator (garbd) against the APRP cluster members.

set -euo pipefail

cluster="${APRP_GALERA_CLUSTER_NAME:-aprp_galera}"
primary_host="${APRP_GALERA_PRIMARY_HOST:-db}"
mirror_host="${APRP_GALERA_MIRROR_HOST:-}"

wait_for_tcp() {
  local host="$1" port="$2" tries="${3:-240}"
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

wait_for_tcp "${primary_host}" "4567" 300

listen_ip="$(hostname -i | awk '{print $1}')"
opts="gmcast.listen_addr=tcp://${listen_ip}:4567"
addr="gcomm://${primary_host}:4567"
if [[ -n "${mirror_host}" ]]; then
  addr="${addr},${mirror_host}:4567"
fi

exec garbd -g "${cluster}" -a "${addr}" -o "${opts}" \
  -n garbd -l -
