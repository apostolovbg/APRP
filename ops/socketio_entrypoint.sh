#!/usr/bin/env bash
# SocketIO entrypoint for the APRP ERP container.

set -euo pipefail

node_bin="$(echo /home/frappe/.nvm/versions/node/*/bin)"
export PATH="${node_bin}:${PATH}"

exec node /home/frappe/frappe-bench/apps/frappe/socketio.js
