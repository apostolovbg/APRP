"""Tests for the APRP Supplier DocType controller."""

import importlib
import unittest


class TestAprpSupplierDocType(unittest.TestCase):
    """Verify the APRP Supplier controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_supplier.aprp_supplier"
        )
        self.assertIn("APRP", module.__doc__ or "")
