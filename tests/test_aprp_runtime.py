"""Runtime scaffolding checks for APRP."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import aprp


class TestAprpRuntime(unittest.TestCase):
    """Verify the runtime stack files stay coherent."""

    def test_package_version_tracks_version_file(self):
        """Ensure the package version comes from the repo version anchor."""
        self.assertEqual(
            Path("VERSION").read_text(encoding="utf-8").strip(),
            aprp.__version__,
        )

    def test_runtime_files_refer_to_the_aprp_hosts(self):
        """Ensure the primary and mirror hostnames are present."""
        runtime_text = "\n".join(
            [
                Path("compose.yaml").read_text(encoding="utf-8"),
                Path("compose.mirror.yaml").read_text(encoding="utf-8"),
                Path("caddy/Caddyfile").read_text(encoding="utf-8"),
                Path("ops/deploy_config.json").read_text(encoding="utf-8"),
                Path("ops/backup_config.json").read_text(encoding="utf-8"),
                Path("docs/system.md").read_text(encoding="utf-8"),
            ]
        )

        self.assertIn("aprp.store", runtime_text)
        self.assertIn("kuche.aprp.store", runtime_text)
        self.assertIn("kotka.aprp.store", runtime_text)
        self.assertIn("APRP_GALERA_NODE", runtime_text)
        self.assertIn("APRP_APP_NAME", runtime_text)

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

    def test_shell_scripts_parse(self):
        """Ensure the runtime shell scripts remain valid Bash."""
        scripts = [
            "ops/backend_entrypoint.sh",
            "ops/socketio_entrypoint.sh",
            "ops/proxysql_entrypoint.sh",
            "ops/mariadb_galera_entrypoint.sh",
            "ops/garbd_entrypoint.sh",
            "ops/site_setup.sh",
            "ops/deploy.sh",
            "ops/deploy_mirror.sh",
            "ops/db_mirror_restore.sh",
            "ops/backup.sh",
        ]

        for script in scripts:
            subprocess.run(["bash", "-n", script], check=True)
