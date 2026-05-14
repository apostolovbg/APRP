"""Tests for the APRP POS Receipt DocType controller."""

import importlib
import unittest


class TestAprpPosReceiptDocType(unittest.TestCase):
    """Verify the APRP POS Receipt controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_pos_receipt.aprp_pos_receipt"
        )
        self.assertIn("APRP", module.__doc__ or "")
