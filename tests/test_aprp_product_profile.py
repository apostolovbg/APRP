"""Tests for the APRP Product Profile DocType controller."""

import importlib
import unittest


class TestAprpProductProfileDocType(unittest.TestCase):
    """Verify the APRP Product Profile controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_product_profile.aprp_product_profile"
        )
        self.assertIn("APRP", module.__doc__ or "")
