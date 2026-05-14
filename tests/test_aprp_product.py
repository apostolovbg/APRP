"""Tests for the APRP Product DocType controller."""

import importlib
import unittest


class TestAprpProductDocType(unittest.TestCase):
    """Verify the APRP Product controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_product.aprp_product"
        )
        self.assertIn("APRP", module.__doc__ or "")
