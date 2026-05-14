"""Tests for the APRP Tax Profile DocType controller."""

import importlib
import unittest


class TestAprpTaxProfileDocType(unittest.TestCase):
    """Verify the APRP Tax Profile controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_tax_profile.aprp_tax_profile"
        )
        self.assertIn("APRP", module.__doc__ or "")
