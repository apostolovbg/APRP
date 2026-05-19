"""Runtime scaffolding checks for APRP."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import unittest
from pathlib import Path

import yaml

import aprp


class TestAprpRuntime(unittest.TestCase):
    """Verify the runtime stack files stay coherent."""

    def _render_opsconfig_env(self, mode: str) -> dict[str, str]:
        """Return shell exports rendered from the tracked ops config."""

        rendered = subprocess.run(
            [
                "python3",
                "ops/opsconfig.py",
                mode,
                "--config",
                "ops/opsconfig.yaml.example",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        env: dict[str, str] = {}
        for line in rendered.splitlines():
            if not line.startswith("export "):
                continue
            assignment = shlex.split(line, posix=True)[1]
            key, value = assignment.split("=", 1)
            env[key] = value
        return env

    def test_package_version_tracks_version_file(self):
        """Ensure the package version comes from the repo version anchor."""
        self.assertEqual(
            Path("VERSION").read_text(encoding="utf-8").strip(),
            aprp.__version__,
        )

    def test_runtime_files_refer_to_the_aprp_hosts(self):
        """Ensure runtime files use config-driven hostnames."""
        runtime_text = "\n".join(
            [
                Path("ops/backend_entrypoint.sh").read_text(encoding="utf-8"),
                Path("ops/site_setup.sh").read_text(encoding="utf-8"),
                Path("ops/opsconfig.py").read_text(encoding="utf-8"),
                Path("ops/opsconfig.yaml.example").read_text(encoding="utf-8"),
                Path("ops/render_workflows.py").read_text(encoding="utf-8"),
                Path("ops/deploy_mirror.sh").read_text(encoding="utf-8"),
                Path("ops/db_mirror_restore.sh").read_text(encoding="utf-8"),
                Path("compose.yaml").read_text(encoding="utf-8"),
                Path("compose.mirror.yaml").read_text(encoding="utf-8"),
                Path("caddy/Caddyfile").read_text(encoding="utf-8"),
                Path(".github/workflows/deploy.yml").read_text(
                    encoding="utf-8"
                ),
                Path(".github/workflows/backup.yml").read_text(
                    encoding="utf-8"
                ),
                Path(".github/workflows/mirror.yml").read_text(
                    encoding="utf-8"
                ),
                Path(".github/workflows/recovery.yml").read_text(
                    encoding="utf-8"
                ),
            ]
        )
        system_text = Path("docs/system.md").read_text(encoding="utf-8")
        install_text = Path("docs/install.md").read_text(encoding="utf-8")
        security_text = Path("docs/security.md").read_text(encoding="utf-8")

        self.assertNotIn("aprp.store", runtime_text)
        self.assertNotIn("kuche.aprp.store", runtime_text)
        self.assertNotIn("kotka.aprp.store", runtime_text)
        self.assertIn("APRP_SERVER_CONTAINER_NAME", runtime_text)
        self.assertIn("APRP_MIRROR_CONTAINER_NAME", runtime_text)
        self.assertIn("APRP_BACKEND_HOST", runtime_text)
        self.assertIn("APRP_CONTACT_EMAIL", runtime_text)
        self.assertIn("APRP_BACKEND_SITE_NAME", runtime_text)
        self.assertIn("APRP_GALERA_NODE", runtime_text)
        self.assertIn("APRP_GALERA_CLUSTER_MEMBERS", runtime_text)
        self.assertIn("APRP_GALERA_MIRROR_HOST", runtime_text)
        self.assertIn("BOOTSTRAP_DB_HOST", runtime_text)
        self.assertIn("APRP_APP_NAME", runtime_text)
        self.assertIn("DB_HOST", runtime_text)
        self.assertIn("DB_PORT", runtime_text)
        self.assertIn("REDIS_CACHE", runtime_text)
        self.assertIn("REDIS_QUEUE", runtime_text)
        self.assertIn("REDIS_SOCKETIO", runtime_text)
        self.assertIn("SOCKETIO_PORT", runtime_text)
        self.assertIn("DEPLOY_GIT_REMOTE", runtime_text)
        self.assertIn("BACKUP_RCLONE_REMOTE", runtime_text)
        self.assertIn("mirror-net", runtime_text)
        self.assertIn("db-mirror-data", runtime_text)
        self.assertIn("mirror-reseed", runtime_text)
        self.assertIn("mirror-rejoin", runtime_text)
        self.assertIn("cluster-status", runtime_text)
        self.assertIn("workflow_dispatch", runtime_text)
        self.assertIn("self-hosted", runtime_text)
        self.assertIn("aprp-primary", runtime_text)
        self.assertIn("aprp-mirror", runtime_text)
        self.assertIn("aprp-server", runtime_text)
        self.assertIn("aprp-mirror", runtime_text)
        self.assertIn("./ops/deploy.sh", runtime_text)
        self.assertIn("./ops/backup.sh", runtime_text)
        self.assertIn("./ops/deploy_mirror.sh", runtime_text)
        self.assertIn("./ops/db_mirror_restore.sh", runtime_text)
        self.assertNotIn("/opt/aprp/checkout", runtime_text)
        self.assertIn("Strict-Transport-Security", runtime_text)
        self.assertIn("reverse_proxy backend:8000", runtime_text)
        self.assertIn("Production Preflight", system_text)
        self.assertIn("docker compose -f compose.yaml config", system_text)
        self.assertIn("DNS-01 Certificate Issuance", system_text)
        self.assertIn("kuche.aprp.store", system_text)
        self.assertIn("kotka.aprp.store", system_text)
        self.assertIn("aprp.store", system_text)
        self.assertIn("aprp-server", system_text)
        self.assertIn("aprp-mirror", system_text)
        self.assertIn("Superhosting.bg", system_text)
        self.assertIn("checkout root", system_text)
        self.assertIn("ops/certs/kuche.aprp.store", system_text)
        self.assertIn("kuche.aprp.store", install_text)
        self.assertIn("kotka.aprp.store", install_text)
        self.assertIn("aprp.store", install_text)
        self.assertIn("Superhosting.bg", install_text)
        self.assertIn("checkout root", install_text)
        self.assertIn("ops/certs/kuche.aprp.store", install_text)
        self.assertIn("manual TXT", install_text)
        self.assertIn("kuche.aprp.store", security_text)
        self.assertIn("kotka.aprp.store", security_text)
        self.assertIn("aprp.store", security_text)
        self.assertIn("Superhosting.bg", security_text)
        self.assertIn("checkout root", security_text)
        self.assertIn("ops/certs/kuche.aprp.store", security_text)
        self.assertIn("manual TXT", security_text)
        self.assertFalse(Path("ops/deploy_config.json").exists())
        self.assertFalse(Path("ops/backup_config.json").exists())

    def test_opsconfig_example_is_structured(self):
        """Ensure the tracked ops config example keeps repo-specific shape."""
        ops_config = yaml.safe_load(
            Path("ops/opsconfig.yaml.example").read_text(encoding="utf-8")
        )

        self.assertIsInstance(ops_config, dict)
        for key in [
            "profile",
            "app_name",
            "server_container_name",
            "mirror_container_name",
            "backend_host",
            "mirror_host",
            "backend_site_name",
            "contact_email",
            "storefront_platform",
            "commerce_platform",
            "db_host",
            "db_port",
            "redis_cache_url",
            "redis_queue_url",
            "redis_socketio_url",
            "socketio_port",
            "galera_cluster_name",
            "galera_cluster_members",
            "galera_primary_host",
            "galera_mirror_host",
            "galera_force_bootstrap",
            "bootstrap_db_host",
            "bootstrap_db_port",
            "deploy_git_remote",
            "deploy_git_branch",
            "deploy_sync_remote",
            "deploy_compose_file",
            "deploy_build_services",
            "deploy_restart_services",
            "backup_local_backup_dir",
            "backup_bench_sites_root",
            "backup_timezone",
            "backup_keep_daily",
            "backup_remote",
            "backup_rclone_conf",
            "backup_bucket",
            "backup_prefix",
            "backup_cap_bytes",
            "backup_target_percent",
            "backup_target_bytes",
            "backup_alert_recipients",
            "backup_max_backup_age_hours",
            "backup_min_free_disk_percent",
            "backup_alert_cooldown_minutes",
            "backup_enable_db_ping",
            "backup_enable_disk_check",
            "backup_enable_offsite_stamp_check",
            "backup_enable_wsrep_probe",
        ]:
            self.assertIn(key, ops_config)
        for key in [
            "app_name",
            "server_container_name",
            "mirror_container_name",
            "backend_host",
            "mirror_host",
            "backend_site_name",
            "contact_email",
            "storefront_platform",
            "commerce_platform",
            "db_host",
            "galera_cluster_name",
            "galera_primary_host",
            "galera_mirror_host",
            "bootstrap_db_host",
            "deploy_git_remote",
            "deploy_git_branch",
            "deploy_compose_file",
            "backup_local_backup_dir",
            "backup_bench_sites_root",
            "backup_timezone",
            "backup_rclone_conf",
            "backup_bucket",
            "backup_prefix",
            "redis_cache_url",
            "redis_queue_url",
            "redis_socketio_url",
        ]:
            self.assertIsInstance(ops_config[key], str)
            self.assertTrue(ops_config[key])
        for key in ["db_port", "socketio_port", "bootstrap_db_port"]:
            self.assertIsInstance(ops_config[key], int)
            self.assertGreater(ops_config[key], 0)
        for key in [
            "galera_cluster_members",
            "deploy_build_services",
            "deploy_restart_services",
            "backup_alert_recipients",
        ]:
            self.assertIsInstance(ops_config[key], list)
            self.assertTrue(ops_config[key])

    def test_opsconfig_instance_is_ignored(self):
        """Ensure the instance config stays local to each installation."""
        gitignore = Path(".gitignore").read_text(encoding="utf-8")

        self.assertIn("ops/opsconfig.yaml", gitignore)

    def test_opsconfig_instance_matches_example_shape(self):
        """Ensure the local config keeps the tracked example shape."""
        instance_path = Path("ops/opsconfig.yaml")
        if not instance_path.exists():
            self.skipTest("Local opsconfig instance is not present.")

        example = yaml.safe_load(
            Path("ops/opsconfig.yaml.example").read_text(encoding="utf-8")
        )
        instance = yaml.safe_load(instance_path.read_text(encoding="utf-8"))

        self.assertEqual(set(example.keys()), set(instance.keys()))

    def test_opsconfig_helper_exports_shell_assignments(self):
        """Ensure the renderer turns the YAML config into shell exports."""
        primary = subprocess.run(
            [
                "python3",
                "ops/opsconfig.py",
                "primary",
                "--config",
                "ops/opsconfig.yaml.example",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        mirror = subprocess.run(
            [
                "python3",
                "ops/opsconfig.py",
                "mirror",
                "--config",
                "ops/opsconfig.yaml.example",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        backup = subprocess.run(
            [
                "python3",
                "ops/opsconfig.py",
                "backup",
                "--config",
                "ops/opsconfig.yaml.example",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        self.assertIn("export APRP_BACKEND_HOST=", primary)
        self.assertIn("export APRP_BACKEND_SITE_NAME=", primary)
        self.assertIn("export SITE_NAME=", primary)
        self.assertIn("export APRP_CONTACT_EMAIL=", primary)
        self.assertIn("export APRP_APP_NAME=", primary)
        self.assertIn("export APRP_SERVER_CONTAINER_NAME=", primary)
        self.assertIn("export DB_HOST=", primary)
        self.assertIn("export DB_PORT=", primary)
        self.assertIn("export REDIS_CACHE=", primary)
        self.assertIn("export REDIS_QUEUE=", primary)
        self.assertIn("export REDIS_SOCKETIO=", primary)
        self.assertIn("export SOCKETIO_PORT=", primary)
        self.assertIn("export APRP_MIRROR_CONTAINER_NAME=", mirror)
        self.assertIn("export BACKUP_SITE_NAME=", backup)
        self.assertIn("export BACKUP_RCLONE_REMOTE=", backup)

    def test_hooks_module_exposes_aprp_metadata(self):
        """Ensure the Frappe hooks module exposes the APRP app contract."""
        import aprp.hooks as hooks

        self.assertEqual("aprp", hooks.app_name)
        self.assertEqual("APRP", hooks.app_title)
        self.assertEqual("APRP", hooks.app_publisher)
        self.assertEqual(
            "Advanced Production Resource Planning",
            hooks.app_description,
        )

    def test_backend_entrypoint_bootstraps_site_on_startup(self):
        """Ensure startup runs the site bootstrap helper before serving."""
        entrypoint = Path("ops/backend_entrypoint.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("site_setup.sh", entrypoint)
        self.assertIn('exec "$@"', entrypoint)

    def test_shell_scripts_parse(self):
        """Ensure the runtime shell scripts remain valid Bash."""
        scripts = [
            "ops/backend_entrypoint.sh",
            "ops/socketio_entrypoint.sh",
            "ops/proxysql_entrypoint.sh",
            "ops/mariadb_galera_entrypoint.sh",
            "ops/garbd_entrypoint.sh",
            "ops/site_setup.sh",
            "ops/deploy_mirror.sh",
            "ops/deploy.sh",
            "ops/db_mirror_restore.sh",
            "ops/backup.sh",
        ]

        for script in scripts:
            subprocess.run(["bash", "-n", script], check=True)

    def test_compose_files_validate_with_rendered_opsconfig(self):
        """Ensure the Compose files validate when Docker is available."""

        if shutil.which("docker") is None:
            self.skipTest("docker compose is not available.")

        try:
            subprocess.run(
                ["docker", "compose", "version"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("docker compose is not available.")

        primary_env = os.environ.copy()
        primary_env.update(self._render_opsconfig_env("primary"))
        primary_env["APRP_COMPOSE_ENV_FILE"] = "ops/env.primary.example"
        mirror_env = os.environ.copy()
        mirror_env.update(self._render_opsconfig_env("mirror"))
        mirror_env["APRP_COMPOSE_ENV_FILE"] = "ops/env.mirror.example"

        subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "config"],
            check=True,
            capture_output=True,
            text=True,
            env=primary_env,
        )
        subprocess.run(
            ["docker", "compose", "-f", "compose.mirror.yaml", "config"],
            check=True,
            capture_output=True,
            text=True,
            env=mirror_env,
        )
