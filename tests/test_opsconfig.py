"""Focused checks for the APRP opsconfig renderer."""

from __future__ import annotations

import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import yaml

import ops.opsconfig as opsconfig


class TestAprpOpsConfig(unittest.TestCase):
    """Verify the config loader exports the runtime contract."""

    def test_example_includes_internal_runtime_keys(self):
        """Ensure the tracked example carries the full config shape."""
        ops_config = yaml.safe_load(
            Path("ops/opsconfig.yaml.example").read_text(encoding="utf-8")
        )

        self.assertEqual("aprp", ops_config["app_name"])
        self.assertEqual("proxysql", ops_config["db_host"])
        self.assertEqual("backend.example.invalid", ops_config["backend_host"])
        self.assertIn("redis_cache_url", ops_config)
        self.assertIn("redis_queue_url", ops_config)
        self.assertIn("redis_socketio_url", ops_config)
        self.assertIn("socketio_port", ops_config)

    def test_renderer_emits_primary_and_mirror_exports(self):
        """Ensure the renderer emits the expected shell exports."""
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

        self.assertIn("export APRP_APP_NAME=", primary)
        self.assertIn("export APRP_BACKEND_HOST=", primary)
        self.assertIn("export DB_HOST=", primary)
        self.assertIn("export REDIS_CACHE=", primary)
        self.assertIn("export SOCKETIO_PORT=", primary)
        self.assertIn("export APRP_GALERA_NODE=", mirror)

    def test_main_renders_primary_exports(self):
        """Ensure main() renders the primary export set."""
        buffer = StringIO()

        self.assertTrue(callable(opsconfig.main))
        self.assertEqual("main", opsconfig.main.__name__)

        with redirect_stdout(buffer):
            exit_code = opsconfig.main(
                [
                    "primary",
                    "--config",
                    "ops/opsconfig.yaml.example",
                ]
            )

        self.assertEqual(0, exit_code)
        self.assertIn("export APRP_APP_NAME=", buffer.getvalue())
        self.assertIn("export APRP_BACKEND_HOST=", buffer.getvalue())
