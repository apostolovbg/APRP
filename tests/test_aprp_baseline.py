"""Neutral APRP baseline sanity tests."""

import unittest
from pathlib import Path


class TestAprpBaseline(unittest.TestCase):
    """Verify the APRP docs and version baseline stay coherent."""

    def test_readme_and_spec_share_the_public_brand(self):
        """Ensure the repo docs present APRP consistently."""
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")
        plan = Path("PLAN.md").read_text(encoding="utf-8")

        self.assertIn("APRP", readme)
        self.assertIn("APRP", spec)
        self.assertIn("APRP", plan)
        self.assertIn("ops/opsconfig.yaml", readme)
        self.assertIn("ops/opsconfig.yaml", spec)
        self.assertIn("Ops Configuration", spec)
        self.assertIn("ops/opsconfig.yaml.example", spec)
        self.assertNotIn("ops/demo_config.json", spec)
        self.assertIn("multi-location", plan)
        self.assertIn("POS", plan)
        self.assertIn("courier", plan)
        self.assertNotIn("Storefront demo milestone", plan)

    def test_version_anchor_is_present(self):
        """Ensure the repo version anchor is available for governance sync."""
        version = Path("VERSION").read_text(encoding="utf-8").strip()

        self.assertEqual("0.4.0", version)
