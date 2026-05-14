"""Tests for the APRP Supplier SKU Mapping DocType controller."""

import importlib
import unittest

MODULE_PATH = (
    "aprp.aprp.doctype."
    "aprp_supplier_sku_mapping."
    "aprp_supplier_sku_mapping"
)


class TestAprpSupplierSkuMapping(unittest.TestCase):
    """Verify the controller imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(MODULE_PATH)
        self.assertIn("APRP", module.__doc__ or "")
