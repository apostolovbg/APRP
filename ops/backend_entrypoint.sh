#!/usr/bin/env bash
# Backend entrypoint for the APRP ERP container.

set -euo pipefail

bench_dir="/home/frappe/frappe-bench"
node_bin="$(echo /home/frappe/.nvm/versions/node/*/bin)"

export PATH="${node_bin}:${PATH}"
cd "${bench_dir}"

if ! python - <<'PY'
import json
import sys
from pathlib import Path

sites_dir = Path("/home/frappe/frappe-bench/sites")
manifest_paths = [
    sites_dir / "assets" / "assets.json",
    sites_dir / "assets" / "assets-rtl.json",
]

missing_assets = []

for manifest_path in manifest_paths:
    if not manifest_path.exists():
        missing_assets.append(str(manifest_path))
        continue
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    for asset_path in manifest_data.values():
        resolved_asset_path = sites_dir / asset_path.lstrip("/")
        if not resolved_asset_path.exists():
            missing_assets.append(str(resolved_asset_path))
            break

if missing_assets:
    print("Missing built assets detected:")
    for asset_path in missing_assets:
        print(asset_path)
    sys.exit(1)
PY
then
    bench build
fi

exec "$@"
