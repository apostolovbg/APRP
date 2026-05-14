"""Tests for the APRP Location Policy DocType controller."""

import importlib
import unittest


class TestAprpLocationPolicyDocType(unittest.TestCase):
    """Verify the APRP Location Policy controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_location_policy.aprp_location_policy"
        )
        self.assertIn("APRP", module.__doc__ or "")
