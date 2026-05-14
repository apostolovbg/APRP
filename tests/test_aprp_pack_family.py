"""Tests for the APRP Pack Family DocType controller."""

import importlib
import unittest


class TestAprpPackFamilyDocType(unittest.TestCase):
    """Verify the APRP Pack Family controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_pack_family.aprp_pack_family"
        )
        self.assertIn("APRP", module.__doc__ or "")
