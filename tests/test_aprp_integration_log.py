"""Tests for the APRP Integration Log DocType controller."""

import importlib
import unittest


class TestAprpIntegrationLogDocType(unittest.TestCase):
    """Verify the APRP Integration Log controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_integration_log.aprp_integration_log"
        )
        self.assertIn("APRP", module.__doc__ or "")
