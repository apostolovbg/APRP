"""Tests for the APRP Courier Adapter DocType controller."""

import importlib
import unittest


class TestAprpCourierAdapterDocType(unittest.TestCase):
    """Verify the APRP Courier Adapter controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_courier_adapter.aprp_courier_adapter"
        )
        self.assertIn("APRP", module.__doc__ or "")
