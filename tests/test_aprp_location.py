"""Tests for the APRP Location DocType controller."""

import importlib
import unittest


class TestAprpLocationDocType(unittest.TestCase):
    """Verify the APRP Location controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_location.aprp_location"
        )
        self.assertIn("APRP", module.__doc__ or "")
