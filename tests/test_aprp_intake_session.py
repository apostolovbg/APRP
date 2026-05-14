"""Tests for the APRP Intake Session DocType controller."""

import importlib
import unittest


class TestAprpIntakeSessionDocType(unittest.TestCase):
    """Verify the APRP Intake Session controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_intake_session.aprp_intake_session"
        )
        self.assertIn("APRP", module.__doc__ or "")
