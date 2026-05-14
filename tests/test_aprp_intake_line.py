"""Tests for the APRP Intake Line DocType controller."""

import importlib
import unittest


class TestAprpIntakeLineDocType(unittest.TestCase):
    """Verify the APRP Intake Line controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_intake_line.aprp_intake_line"
        )
        self.assertIn("APRP", module.__doc__ or "")
