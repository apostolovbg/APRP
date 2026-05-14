"""Tests for the APRP Warehouse Policy DocType controller."""

import importlib
import unittest


class TestAprpWarehousePolicyDocType(unittest.TestCase):
    """Verify the APRP Warehouse Policy controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_warehouse_policy.aprp_warehouse_policy"
        )
        self.assertIn("APRP", module.__doc__ or "")
