"""Tests for the APRP Price List DocType controller."""

import importlib
import unittest


class TestAprpPriceListDocType(unittest.TestCase):
    """Verify the APRP Price List controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_price_list.aprp_price_list"
        )
        self.assertIn("APRP", module.__doc__ or "")
