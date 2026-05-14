"""Tests for the APRP Courier Event DocType controller."""

import importlib
import unittest


class TestAprpCourierEventDocType(unittest.TestCase):
    """Verify the APRP Courier Event controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_courier_event.aprp_courier_event"
        )
        self.assertIn("APRP", module.__doc__ or "")
