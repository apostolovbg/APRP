#!/usr/bin/env python3
"""Render APRP opsconfig values into shell exports."""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

import yaml


def _load_config(path: Path) -> dict:
    """Load and validate the tracked APRP ops config mapping."""

    if not path.exists():
        raise SystemExit(f"Config file is missing: {path}")

    config_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(config_data, dict):
        raise SystemExit(f"Config file must contain a mapping: {path}")
    return config_data


def _require(config_data: dict, key: str):
    """Return a required config value or fail fast."""

    if key not in config_data or config_data[key] in (None, ""):
        raise SystemExit(f"Missing required config key: {key}")
    return config_data[key]


def _emit(name: str, value: object) -> None:
    """Print one shell export line for a config-derived value."""

    print(f"export {name}={shlex.quote(str(value))}")


def _emit_joined(name: str, values: object, separator: str) -> None:
    """Print a joined shell export for list-valued config fields."""

    if not isinstance(values, list):
        raise SystemExit(f"{name} must be a list")
    _emit(name, separator.join(str(item) for item in values))


def _emit_bool(name: str, value: object) -> None:
    """Print a shell export using APRP's numeric boolean convention."""

    _emit(name, "1" if bool(value) else "0")


def _primary_exports(config_data: dict) -> None:
    """Emit the primary-host shell exports derived from config."""

    _emit("APRP_APP_NAME", _require(config_data, "app_name"))
    backend_site_name = _require(config_data, "backend_site_name")
    backend_host = _require(config_data, "backend_host")
    contact_email = _require(config_data, "contact_email")
    cluster_members = _require(config_data, "galera_cluster_members")

    if backend_host not in cluster_members:
        raise SystemExit("galera_cluster_members must include backend_host")
    if _require(config_data, "galera_mirror_host") not in cluster_members:
        raise SystemExit(
            "galera_cluster_members must include galera_mirror_host"
        )

    _emit("APRP_BACKEND_SITE_NAME", backend_site_name)
    _emit("SITE_NAME", backend_site_name)
    _emit("FRAPPE_SITE_NAME_HEADER", backend_site_name)
    _emit("FRAPPE_DEFAULT_SITE", backend_site_name)
    _emit("APRP_BACKEND_HOST", backend_host)
    _emit("APRP_CONTACT_EMAIL", contact_email)
    _emit("APRP_APP_EMAIL", contact_email)
    _emit("DB_HOST", _require(config_data, "db_host"))
    _emit("DB_PORT", _require(config_data, "db_port"))
    _emit("REDIS_CACHE", _require(config_data, "redis_cache_url"))
    _emit("REDIS_QUEUE", _require(config_data, "redis_queue_url"))
    _emit("REDIS_SOCKETIO", _require(config_data, "redis_socketio_url"))
    _emit("SOCKETIO_PORT", _require(config_data, "socketio_port"))
    _emit(
        "APRP_GALERA_CLUSTER_NAME",
        _require(config_data, "galera_cluster_name"),
    )
    _emit_joined(
        "APRP_GALERA_CLUSTER_MEMBERS",
        cluster_members,
        ",",
    )
    _emit(
        "APRP_GALERA_PRIMARY_HOST",
        _require(config_data, "galera_primary_host"),
    )
    _emit(
        "APRP_GALERA_MIRROR_HOST",
        _require(config_data, "galera_mirror_host"),
    )
    _emit_bool(
        "APRP_GALERA_FORCE_BOOTSTRAP",
        _require(config_data, "galera_force_bootstrap"),
    )
    _emit("BOOTSTRAP_DB_HOST", _require(config_data, "bootstrap_db_host"))
    _emit("BOOTSTRAP_DB_PORT", _require(config_data, "bootstrap_db_port"))


def _mirror_exports(config_data: dict) -> None:
    """Emit the mirror-host shell exports derived from config."""

    _emit("APRP_GALERA_NODE", "db-mirror")
    _emit(
        "APRP_GALERA_CLUSTER_NAME",
        _require(config_data, "galera_cluster_name"),
    )
    _emit_joined(
        "APRP_GALERA_CLUSTER_MEMBERS",
        _require(config_data, "galera_cluster_members"),
        ",",
    )
    _emit(
        "APRP_GALERA_PRIMARY_HOST",
        _require(config_data, "galera_primary_host"),
    )
    _emit(
        "APRP_GALERA_MIRROR_HOST",
        _require(config_data, "galera_mirror_host"),
    )
    _emit_bool(
        "APRP_GALERA_FORCE_BOOTSTRAP",
        _require(config_data, "galera_force_bootstrap"),
    )


def _deploy_exports(config_data: dict) -> None:
    """Emit the deploy shell exports derived from config."""

    _primary_exports(config_data)
    _emit("DEPLOY_SITE_NAME", _require(config_data, "backend_site_name"))
    _emit("DEPLOY_GIT_REMOTE", _require(config_data, "deploy_git_remote"))
    _emit("DEPLOY_GIT_BRANCH", _require(config_data, "deploy_git_branch"))
    _emit_bool(
        "DEPLOY_GIT_SYNC_REMOTE",
        _require(config_data, "deploy_sync_remote"),
    )
    _emit("DEPLOY_COMPOSE_FILE", _require(config_data, "deploy_compose_file"))
    _emit_joined(
        "DEPLOY_BUILD_SERVICES",
        _require(config_data, "deploy_build_services"),
        " ",
    )
    _emit_joined(
        "DEPLOY_RESTART_SERVICES",
        _require(config_data, "deploy_restart_services"),
        " ",
    )


def _backup_exports(config_data: dict) -> None:
    """Emit the backup shell exports derived from config."""

    _emit("BACKUP_SITE_NAME", _require(config_data, "backend_site_name"))
    _emit(
        "BACKUP_LOCAL_BACKUP_DIR",
        _require(config_data, "backup_local_backup_dir"),
    )
    _emit(
        "BACKUP_BENCH_SITES_ROOT",
        _require(config_data, "backup_bench_sites_root"),
    )
    _emit("BACKUP_TZ", _require(config_data, "backup_timezone"))
    _emit("BACKUP_KEEP_DAILY", _require(config_data, "backup_keep_daily"))
    _emit("BACKUP_RCLONE_REMOTE", _require(config_data, "backup_remote"))
    _emit("BACKUP_RCLONE_CONF", _require(config_data, "backup_rclone_conf"))
    _emit("BACKUP_B2_BUCKET", _require(config_data, "backup_bucket"))
    _emit("BACKUP_B2_PREFIX", _require(config_data, "backup_prefix"))
    _emit("BACKUP_B2_CAP_BYTES", _require(config_data, "backup_cap_bytes"))
    _emit(
        "BACKUP_B2_TARGET_PERCENT",
        _require(config_data, "backup_target_percent"),
    )
    if config_data.get("backup_target_bytes") not in (None, ""):
        _emit("BACKUP_B2_TARGET_BYTES", config_data.get("backup_target_bytes"))
    _emit_joined(
        "BACKUP_ALERT_RECIPIENTS",
        _require(config_data, "backup_alert_recipients"),
        ",",
    )
    _emit(
        "BACKUP_MAX_BACKUP_AGE_HOURS",
        _require(config_data, "backup_max_backup_age_hours"),
    )
    _emit(
        "BACKUP_MIN_FREE_DISK_PERCENT",
        _require(config_data, "backup_min_free_disk_percent"),
    )
    _emit(
        "BACKUP_ALERT_COOLDOWN_MINUTES",
        _require(config_data, "backup_alert_cooldown_minutes"),
    )
    _emit_bool(
        "BACKUP_ENABLE_DB_PING",
        _require(config_data, "backup_enable_db_ping"),
    )
    _emit_bool(
        "BACKUP_ENABLE_DISK_CHECK",
        _require(config_data, "backup_enable_disk_check"),
    )
    _emit_bool(
        "BACKUP_ENABLE_OFFSITE_STAMP_CHECK",
        _require(config_data, "backup_enable_offsite_stamp_check"),
    )
    _emit_bool(
        "BACKUP_ENABLE_WSREP_PROBE",
        _require(config_data, "backup_enable_wsrep_probe"),
    )


def main(argv: list[str]) -> int:
    """Render the requested APRP config mode to shell exports."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=["primary", "mirror", "deploy", "backup"],
    )
    parser.add_argument(
        "--config",
        default="ops/opsconfig.yaml",
        help="Path to the APRP ops config file.",
    )
    args = parser.parse_args(argv)

    config_data = _load_config(Path(args.config))
    if args.mode == "primary":
        _primary_exports(config_data)
    elif args.mode == "mirror":
        _mirror_exports(config_data)
    elif args.mode == "deploy":
        _deploy_exports(config_data)
    elif args.mode == "backup":
        _backup_exports(config_data)
    else:
        raise SystemExit(f"Unsupported mode: {args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
