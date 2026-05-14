"""Release summary checks for APRP."""

from __future__ import annotations

import unittest
from pathlib import Path


class TestAprpReleaseSummary(unittest.TestCase):
    """Verify the release summary stays honest and documented."""

    def test_release_summary_covers_release_gate_language(self):
        """Ensure the release summary names the current release contract."""

        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")
        release = Path("docs/release.md").read_text(encoding="utf-8")
        normalized = " ".join(release.split())

        self.assertIn("docs/release.md", readme)
        self.assertIn("docs/release.md", spec)
        self.assertIn("## Overview", release)
        self.assertIn("## Release Summary", release)
        self.assertIn("## Known Limitations", release)
        self.assertIn("## Validation", release)
        self.assertIn("1.0.0 production-grade and demo-ready", release)
        self.assertIn("aprp.aprp.runtime_services", release)
        self.assertIn("aprp.aprp.storefront_services", release)
        self.assertIn("aprp.aprp.showcase_services", release)
        self.assertIn("aprp.aprp.pos_services", release)
        self.assertIn("aprp.aprp.courier_services", release)
        self.assertIn("aprp.aprp.accounting_services", release)
        self.assertIn("ops/opsconfig.yaml", release)
        self.assertIn("unrestricted anonymous ERP access", normalized)
        self.assertIn("full multi-tenant automation", normalized)
        self.assertIn(
            "Full business integration work is quoted separately", release
        )
        self.assertGreaterEqual(
            sum(1 for line in release.splitlines() if line.startswith("## ")),
            4,
        )
