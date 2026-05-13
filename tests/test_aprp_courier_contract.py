"""Core APRP courier contract tests."""

import unittest
from pathlib import Path

from aprp.aprp import (
    COURIER_EVENT_TYPES,
    COURIER_SERVICE_MODES,
    COURIER_TARGETS,
    CourierCapability,
    CourierDispatchBatch,
    CourierEvent,
    CourierShipment,
    CourierSummary,
    build_courier_summary,
)


class TestAprpCourierContract(unittest.TestCase):
    """Verify courier, COD, and return handling stays explicit."""

    def test_courier_capabilities_keep_service_modes_explicit(self):
        """Keep destination and COD rules clear."""
        capability = CourierCapability(
            courier_name="Speedy",
            supports_international=True,
        )

        self.assertEqual(("Speedy", "Econt"), COURIER_TARGETS)
        self.assertEqual(
            (
                "Office Pickup",
                "Address Delivery",
                "Store Pickup",
            ),
            COURIER_SERVICE_MODES,
        )
        self.assertEqual(
            (
                "label_created",
                "handed_off",
                "delivered",
                "cod_collected",
                "payout_received",
                "returned",
                "exception",
            ),
            COURIER_EVENT_TYPES,
        )
        self.assertTrue(capability.supports_destination("BG"))
        self.assertTrue(capability.supports_destination("DE"))
        self.assertTrue(capability.supports_service_mode("Office Pickup"))
        self.assertTrue(
            capability.can_create_shipment("BG", "Address Delivery")
        )
        self.assertTrue(capability.can_offer_cod("BG", "Address Delivery"))
        self.assertFalse(capability.can_offer_cod("DE", "Address Delivery"))
        self.assertFalse(capability.can_create_shipment("DE", "Unknown"))

    def test_courier_shipments_and_events_keep_reconciliation_explicit(
        self,
    ):
        """Ensure shipment state and courier events stay reviewable."""
        shipment = CourierShipment(
            shipment_id="SHIP-2026-0001",
            order_id="SO-2026-0001",
            courier_name="Speedy",
            service_mode="Address Delivery",
            destination_country="BG",
            shipment_state="Delivered",
            label_reference="LBL-2026-0001",
            tracking_number="TRK-2026-0001",
            cod_state="Collected",
            payout_state="Pending",
            return_state="None",
        )
        event = CourierEvent(
            event_id="EV-2026-0001",
            shipment_id="SHIP-2026-0001",
            courier_name="Speedy",
            event_type="exception",
            occurred_at="2026-05-13T10:00:00+02:00",
            event_state="Review",
        )
        batch = CourierDispatchBatch(
            batch_id="BATCH-2026-0001",
            courier_name="Speedy",
            shipments=(shipment,),
            events=(event,),
        )

        self.assertEqual(
            "Speedy|SO-2026-0001|SHIP-2026-0001",
            shipment.shipment_key(),
        )
        self.assertTrue(shipment.is_domestic())
        self.assertTrue(shipment.has_label())
        self.assertTrue(shipment.has_tracking())
        self.assertFalse(shipment.is_cod_pending())
        self.assertFalse(shipment.needs_review())
        self.assertTrue(event.is_exception())
        self.assertFalse(event.affects_payment())
        self.assertTrue(batch.review_required())

        summary = build_courier_summary(batch)

        self.assertIsInstance(summary, CourierSummary)
        self.assertEqual(1, summary.shipment_count)
        self.assertEqual(1, summary.event_count)
        self.assertEqual(1, summary.tracking_count)
        self.assertEqual(0, summary.cod_pending_count)
        self.assertEqual(0, summary.return_count)
        self.assertEqual(1, summary.exception_count)
        self.assertTrue(summary.review_required)
        self.assertFalse(summary.is_ready_to_close())

    def test_courier_event_and_return_helpers_stay_explicit(self):
        """Ensure return and event helper methods stay visible."""
        return_shipment = CourierShipment(
            shipment_id="SHIP-2026-0002",
            order_id="SO-2026-0002",
            courier_name="Econt",
            service_mode="Store Pickup",
            destination_country="BG",
            shipment_state="Returned",
            label_reference="LBL-2026-0002",
            tracking_number="TRK-2026-0002",
            cod_state="Pending",
            payout_state="Settled",
            return_state="Returned",
        )
        return_event = CourierEvent(
            event_id="EV-2026-0002",
            shipment_id="SHIP-2026-0002",
            courier_name="Econt",
            event_type="returned",
            occurred_at="2026-05-13T11:00:00+02:00",
            event_state="Recorded",
        )

        self.assertEqual(
            "Econt|SHIP-2026-0002|EV-2026-0002",
            return_event.event_key(),
        )
        self.assertTrue(return_event.affects_return())
        self.assertFalse(return_event.affects_payment())
        self.assertTrue(return_shipment.has_return())
        self.assertTrue(return_shipment.is_closed())
        self.assertTrue(return_shipment.is_domestic())

    def test_courier_docs_cover_the_adapter_contract(self):
        """Ensure the courier guide names the adapter contract directly."""
        couriers = Path("docs/couriers.md").read_text(encoding="utf-8")

        for token in [
            "aprp.aprp.courier_contract",
            "Courier Capability",
            "Courier Shipment",
            "Courier Event",
            "Courier Dispatch Batch",
            "Courier Summary",
            "Speedy",
            "Econt",
            "COD",
            "returns",
        ]:
            self.assertIn(token, couriers)

    def test_contract_symbols_stay_explicit(self):
        """Ensure the exported courier symbols stay named directly."""
        self.assertEqual(CourierCapability.__name__, "CourierCapability")
        self.assertEqual(CourierEvent.__name__, "CourierEvent")
        self.assertEqual(CourierShipment.__name__, "CourierShipment")
        self.assertEqual(
            CourierDispatchBatch.__name__,
            "CourierDispatchBatch",
        )
        self.assertEqual(CourierSummary.__name__, "CourierSummary")
        self.assertEqual(
            build_courier_summary.__name__,
            "build_courier_summary",
        )
