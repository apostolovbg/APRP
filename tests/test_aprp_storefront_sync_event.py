"""Tests for the APRP Storefront Sync Event DocType controller."""

import importlib
import unittest

MODULE_PATH = (
    "aprp.aprp.doctype."
    "aprp_storefront_sync_event."
    "aprp_storefront_sync_event"
)


class TestAprpStorefrontSyncEvent(unittest.TestCase):
    """Verify the controller imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(MODULE_PATH)
        self.assertIn("APRP", module.__doc__ or "")
