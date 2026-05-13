"""Tests for the APRP workflow wrapper generator."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ops.render_workflows as render_workflows


class TestRenderWorkflows(unittest.TestCase):
    """Verify the workflow wrapper generator stays in sync."""

    def test_module_exposes_expected_wrappers(self):
        """Ensure the generator keeps the tracked wrapper set."""
        self.assertIn("deploy.yml", render_workflows.WORKFLOWS)
        self.assertIn("backup.yml", render_workflows.WORKFLOWS)
        self.assertIn("mirror.yml", render_workflows.WORKFLOWS)
        self.assertIn("recovery.yml", render_workflows.WORKFLOWS)

    def test_main_writes_and_checks_wrappers(self):
        """Ensure the generator can write and verify tracked wrappers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(
                0,
                render_workflows.main(["--output-dir", temp_dir]),
            )

            temp_root = Path(temp_dir)
            for name in render_workflows.WORKFLOWS:
                self.assertTrue((temp_root / name).exists())

            self.assertEqual(
                0,
                render_workflows.main(
                    [
                        "--check",
                        "--output-dir",
                        temp_dir,
                    ]
                ),
            )
