"""Tests for the APRP Courier Shipment DocType controller."""

import importlib
import unittest


class TestAprpCourierShipmentDocType(unittest.TestCase):
    """Verify the APRP Courier Shipment controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_courier_shipment.aprp_courier_shipment"
        )
        self.assertIn("APRP", module.__doc__ or "")
