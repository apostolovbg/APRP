"""Neutral APRP baseline sanity tests."""

import unittest
from pathlib import Path


class TestAprpBaseline(unittest.TestCase):
    """Verify the public APRP docs and version baseline stay coherent."""

    def test_readme_and_spec_share_the_public_brand(self):
        """Ensure the public docs present APRP consistently."""
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")

        self.assertIn("APRP", readme)
        self.assertIn("APRP", spec)
        self.assertIn("aprp.store", readme)
        self.assertIn("kuche.aprp.store", readme)
        self.assertIn("aprp.store", spec)
        self.assertIn("kuche.aprp.store", spec)

    def test_version_anchor_is_present(self):
        """Ensure the repo version anchor is available for governance sync."""
        version = Path("VERSION").read_text(encoding="utf-8").strip()

        self.assertEqual("0.4.0", version)
