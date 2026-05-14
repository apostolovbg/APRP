"""Tests for the APRP Customer DocType controller."""

import importlib
import unittest


class TestAprpCustomerDocType(unittest.TestCase):
    """Verify the APRP Customer controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_customer.aprp_customer"
        )
        self.assertIn("APRP", module.__doc__ or "")
