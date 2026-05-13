"""Install validation and repository hygiene checks for APRP."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import yaml


class TestAprpInstallValidation(unittest.TestCase):
    """Verify generalized install profiles and repo hygiene."""

    def test_opsconfig_accepts_variant_profile(self):
        """Ensure opsconfig renders an arbitrary valid config variant."""
        example = yaml.safe_load(
            Path("ops/opsconfig.yaml.example").read_text(encoding="utf-8")
        )
        variant = deepcopy(example)
        variant.update(
            {
                "app_name": "aprp-variant",
                "backend_host": "backend-variant.example.invalid",
                "mirror_host": "mirror-variant.example.invalid",
                "backend_site_name": "site-variant.example.invalid",
                "contact_email": "ops-variant@example.invalid",
                "db_host": "proxysql-variant",
                "deploy_git_remote": "upstream",
                "deploy_git_branch": "develop",
                "backup_remote": "variant-b2",
            }
        )
        variant["galera_cluster_members"] = [
            "backend-variant.example.invalid",
            "mirror-variant.example.invalid",
        ]
        variant["galera_primary_host"] = "backend-variant.example.invalid"
        variant["galera_mirror_host"] = "mirror-variant.example.invalid"

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "opsconfig.yaml"
            config_path.write_text(
                yaml.safe_dump(variant, sort_keys=False),
                encoding="utf-8",
            )

            primary = subprocess.run(
                [
                    "python3",
                    "ops/opsconfig.py",
                    "primary",
                    "--config",
                    str(config_path),
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
                    str(config_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            deploy = subprocess.run(
                [
                    "python3",
                    "ops/opsconfig.py",
                    "deploy",
                    "--config",
                    str(config_path),
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
                    str(config_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

        self.assertIn("export APRP_APP_NAME=aprp-variant", primary)
        self.assertIn(
            "export APRP_BACKEND_HOST=backend-variant.example.invalid",
            primary,
        )
        self.assertIn(
            "export APRP_GALERA_CLUSTER_MEMBERS="
            "backend-variant.example.invalid,mirror-variant.example.invalid",
            primary,
        )
        self.assertIn("export APRP_GALERA_NODE=db-mirror", mirror)
        self.assertIn("export DEPLOY_GIT_REMOTE=upstream", deploy)
        self.assertIn("export DEPLOY_GIT_BRANCH=develop", deploy)
        self.assertIn(
            "export DEPLOY_SITE_NAME=site-variant.example.invalid",
            deploy,
        )
        self.assertIn("export BACKUP_RCLONE_REMOTE=variant-b2", backup)
        self.assertIn(
            "export BACKUP_SITE_NAME=site-variant.example.invalid",
            backup,
        )

    def test_repo_surface_has_no_banned_identity_or_secret_markers(self):
        """Ensure the product surfaces stay clear of banned strings."""
        surface_patterns = [
            "README.md",
            "SPEC.md",
            "PLAN.md",
            "docs/**/*.md",
            "ops/**/*.py",
            "ops/**/*.sh",
            "ops/**/*.yaml",
            "ops/**/*.yml",
            "ops/**/*.json",
            "caddy/Caddyfile",
            "compose*.yaml",
            ".github/workflows/*.yml",
            "aprp/**/*.py",
        ]
        collected = []
        seen = set()
        for pattern in surface_patterns:
            for path in Path(".").glob(pattern):
                if not path.is_file() or path in seen:
                    continue
                seen.add(path)
                collected.append(path.read_text(encoding="utf-8"))

        combined = "\n".join(collected)
        for banned in [
            r"\bGCV\b",
            r"\bgoblin\b",
            r"\bcard\b",
            r"\bbooster\b",
            r"\bTCG\b",
            "BEGIN PRIVATE KEY",
            "ghp_",
            "xox[baprs]-",
        ]:
            self.assertNotRegex(combined, banned)
