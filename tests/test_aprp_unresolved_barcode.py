"""Tests for the APRP Unresolved Barcode DocType controller."""

import importlib
import unittest


class TestAprpUnresolvedBarcodeDocType(unittest.TestCase):
    """Verify the APRP Unresolved Barcode controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_unresolved_barcode.aprp_unresolved_barcode"
        )
        self.assertIn("APRP", module.__doc__ or "")
