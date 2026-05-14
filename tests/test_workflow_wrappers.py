"""Checks for the generated APRP GitHub workflow wrappers."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

WORKFLOW_FILES = [
    Path(".github/workflows/deploy.yml"),
    Path(".github/workflows/backup.yml"),
    Path(".github/workflows/mirror.yml"),
    Path(".github/workflows/recovery.yml"),
]


class TestAprpWorkflowWrappers(unittest.TestCase):
    """Verify the generated workflow wrappers stay repo-owned."""

    def test_workflow_wrappers_are_present(self):
        """Ensure the generated workflow wrappers are tracked."""
        for path in WORKFLOW_FILES:
            self.assertTrue(path.exists(), path)

    def test_workflow_wrappers_match_generator_output(self):
        """Ensure the tracked wrappers match the generator output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run(
                [
                    "python3",
                    "ops/render_workflows.py",
                    "--output-dir",
                    temp_dir,
                ],
                check=True,
            )

            temp_root = Path(temp_dir)
            for path in WORKFLOW_FILES:
                generated = temp_root / path.name
                self.assertEqual(
                    path.read_text(encoding="utf-8"),
                    generated.read_text(encoding="utf-8"),
                )

    def test_workflow_wrappers_stay_host_driven(self):
        """Ensure the wrappers stay on host-managed paths and scripts."""
        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in WORKFLOW_FILES
        )

        for banned in [
            "aprp.store",
            "kuche.aprp.store",
            "kotka.aprp.store",
            "/opt/aprp/APRP",
        ]:
            self.assertNotIn(banned, combined)

        self.assertIn("/opt/aprp/checkout", combined)
        self.assertIn("self-hosted", combined)
        self.assertIn("aprp-primary", combined)
        self.assertIn("aprp-mirror", combined)
        self.assertIn("workflow_dispatch", combined)
        self.assertIn("./ops/deploy.sh", combined)
        self.assertIn("./ops/backup.sh", combined)
        self.assertIn("./ops/deploy_mirror.sh", combined)
        self.assertIn("./ops/db_mirror_restore.sh", combined)
