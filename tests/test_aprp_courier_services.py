"""Courier service helper tests for APRP."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import aprp.aprp as package
from aprp.aprp import (
    COURIER_SERVICE_EVENT_TYPES,
    COURIER_SERVICE_TARGETS,
    CourierAdapter,
    CourierDispatchBatchDraft,
    CourierEcontAdapter,
    CourierEventDraft,
    CourierShipmentDraft,
    CourierSimulatorAdapter,
    CourierSpeedyAdapter,
    CourierSummaryDraft,
    CourierTrackingReferenceDraft,
    build_courier_dispatch_batch_doc,
    build_courier_event_doc,
    build_courier_shipment_doc,
    build_courier_summary_doc,
    select_courier_adapters,
    shipment_validation_blockers,
    validate_courier_shipment,
)


class TestAprpCourierServices(unittest.TestCase):
    """Verify the courier service layer stays explicit."""

    def test_package_exports_courier_service_helpers(self):
        """Ensure the package exposes the courier service layer."""

        module = importlib.import_module("aprp.aprp.courier_services")
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")
        docs = Path("docs/couriers.md").read_text(encoding="utf-8")

        self.assertIn("APRP", module.__doc__ or "")
        self.assertIn("aprp.aprp.courier_services", readme)
        self.assertIn("aprp.aprp.courier_services", spec)
        self.assertIn("aprp.aprp.courier_services", docs)
        self.assertIs(package.CourierAdapter, CourierAdapter)
        self.assertIs(
            package.CourierDispatchBatchDraft,
            CourierDispatchBatchDraft,
        )
        self.assertIs(package.CourierEcontAdapter, CourierEcontAdapter)
        self.assertIs(package.CourierEventDraft, CourierEventDraft)
        self.assertIs(package.CourierShipmentDraft, CourierShipmentDraft)
        self.assertIs(package.CourierSimulatorAdapter, CourierSimulatorAdapter)
        self.assertIs(package.CourierSpeedyAdapter, CourierSpeedyAdapter)
        self.assertIs(package.CourierSummaryDraft, CourierSummaryDraft)
        self.assertIs(
            package.CourierTrackingReferenceDraft,
            CourierTrackingReferenceDraft,
        )
        self.assertIs(
            package.build_courier_dispatch_batch_doc,
            build_courier_dispatch_batch_doc,
        )
        self.assertIs(package.build_courier_event_doc, build_courier_event_doc)
        self.assertIs(
            package.build_courier_shipment_doc,
            build_courier_shipment_doc,
        )
        self.assertIs(
            package.build_courier_summary_doc,
            build_courier_summary_doc,
        )
        self.assertIs(
            package.select_courier_adapters,
            select_courier_adapters,
        )
        self.assertIs(
            package.shipment_validation_blockers,
            shipment_validation_blockers,
        )
        self.assertIs(
            package.validate_courier_shipment,
            validate_courier_shipment,
        )
        self.assertEqual(
            module.COURIER_EVENT_TYPES,
            COURIER_SERVICE_EVENT_TYPES,
        )
        self.assertEqual(
            module.DEFAULT_COURIER_TARGETS,
            COURIER_SERVICE_TARGETS,
        )
        self.assertEqual(
            tuple(
                adapter.courier_name
                for adapter in module.DEFAULT_COURIER_ADAPTERS
            ),
            ("Speedy", "Econt"),
        )
        self.assertEqual(CourierAdapter.__name__, "CourierAdapter")
        self.assertEqual(
            CourierAdapter.allows_cod_for_destination.__name__,
            "allows_cod_for_destination",
        )
        self.assertEqual(
            CourierAdapter.supports_order.__name__,
            "supports_order",
        )
        self.assertEqual(
            CourierAdapter.supports_service_mode.__name__,
            "supports_service_mode",
        )
        self.assertEqual(
            CourierAdapter.validate_shipment.__name__,
            "validate_shipment",
        )
        self.assertEqual(
            CourierDispatchBatchDraft.__name__,
            "CourierDispatchBatchDraft",
        )
        self.assertEqual(CourierEcontAdapter.__name__, "CourierEcontAdapter")
        self.assertEqual(CourierEventDraft.__name__, "CourierEventDraft")
        self.assertEqual(CourierShipmentDraft.__name__, "CourierShipmentDraft")
        self.assertEqual(CourierShipmentDraft.has_label.__name__, "has_label")
        self.assertEqual(
            CourierShipmentDraft.to_contract.__name__,
            "to_contract",
        )
        self.assertEqual(
            CourierSimulatorAdapter.__name__,
            "CourierSimulatorAdapter",
        )
        self.assertEqual(
            CourierSimulatorAdapter.sample_shipments.__name__,
            "sample_shipments",
        )
        self.assertEqual(CourierSpeedyAdapter.__name__, "CourierSpeedyAdapter")
        self.assertEqual(CourierSummaryDraft.__name__, "CourierSummaryDraft")
        self.assertEqual(
            CourierSummaryDraft.to_contract.__name__,
            "to_contract",
        )
        self.assertEqual(
            CourierEventDraft.to_contract.__name__,
            "to_contract",
        )
        self.assertEqual(
            CourierDispatchBatchDraft.to_contract.__name__,
            "to_contract",
        )
        self.assertEqual(
            CourierTrackingReferenceDraft.__name__,
            "CourierTrackingReferenceDraft",
        )
        self.assertTrue(callable(build_courier_dispatch_batch_doc))
        self.assertTrue(callable(build_courier_event_doc))
        self.assertTrue(callable(build_courier_shipment_doc))
        self.assertTrue(callable(build_courier_summary_doc))
        self.assertTrue(callable(select_courier_adapters))
        self.assertTrue(callable(shipment_validation_blockers))
        self.assertTrue(callable(validate_courier_shipment))

    def test_simulator_adapter_builds_shipment_drafts_and_summary(self):
        """Ensure the simulator adapter builds proof-path shipment data."""

        simulator = CourierSimulatorAdapter()
        shipments = simulator.sample_shipments()
        shipment_draft = simulator.build_courier_shipment_doc(shipments[0])
        review_shipment_draft = simulator.build_courier_shipment_doc(
            shipments[1]
        )
        batch = simulator.build_courier_dispatch_batch_doc(
            batch_id="BATCH-2026-1001",
            shipments=shipments,
            notes="Courier proof run",
        )
        summary = simulator.build_courier_summary_doc(batch)

        self.assertIsInstance(simulator, CourierAdapter)
        self.assertEqual(2, len(shipments))
        self.assertEqual("SHIP-2026-0001", shipment_draft.shipment_id)
        self.assertEqual("Speedy", shipment_draft.courier_name)
        self.assertEqual("TRK-2026-0001", shipment_draft.tracking_number)
        self.assertTrue(shipment_draft.has_tracking())
        self.assertFalse(shipment_draft.needs_review())
        self.assertEqual(
            "TRK-2026-0001",
            shipment_draft.to_doc()["tracking_reference"]["tracking_number"],
        )
        self.assertEqual("SHIP-2026-0002", review_shipment_draft.shipment_id)
        self.assertTrue(review_shipment_draft.needs_review())
        self.assertEqual("Returned", review_shipment_draft.return_state)
        self.assertEqual("In Progress", batch.status)
        self.assertEqual(2, batch.shipment_count())
        self.assertEqual(2, batch.event_count())
        self.assertEqual(2, batch.tracking_count())
        self.assertEqual(1, batch.return_count())
        self.assertEqual(1, batch.exception_count())
        self.assertTrue(batch.review_required)
        self.assertFalse(batch.is_clear())
        self.assertEqual(2, summary.shipment_count)
        self.assertEqual(2, summary.event_count)
        self.assertEqual(2, summary.tracking_count)
        self.assertEqual(1, summary.cod_pending_count)
        self.assertEqual(1, summary.return_count)
        self.assertEqual(1, summary.exception_count)
        self.assertTrue(summary.review_required)
        self.assertEqual("Review Required", summary.operator_state)
        self.assertFalse(summary.is_ready_to_close())

    def test_adapter_shells_keep_selection_rules_explicit(self):
        """Ensure the courier shells keep capability selection visible."""

        speedy = CourierSpeedyAdapter()
        econt = CourierEcontAdapter()
        bg_adapters = select_courier_adapters(
            "BG",
            "Address Delivery",
            requires_cod=True,
        )
        de_adapters = select_courier_adapters(
            "DE",
            "Address Delivery",
        )

        self.assertTrue(speedy.supports_destination("DE"))
        self.assertFalse(econt.supports_destination("DE"))
        self.assertTrue(speedy.can_offer_cod("BG", "Address Delivery"))
        self.assertTrue(econt.can_offer_cod("BG", "Address Delivery"))
        self.assertFalse(econt.can_create_shipment("DE", "Address Delivery"))
        self.assertEqual(
            ("Speedy", "Econt"),
            tuple(adapter.courier_name for adapter in bg_adapters),
        )
        self.assertEqual(
            ("Speedy",),
            tuple(adapter.courier_name for adapter in de_adapters),
        )
        self.assertTrue(
            validate_courier_shipment(
                {
                    "shipment_id": "SHIP-2026-1003",
                    "order_id": "SO-2026-1003",
                    "courier_name": "Speedy",
                    "service_mode": "Address Delivery",
                    "destination_country": "BG",
                    "shipment_state": "Delivered",
                    "label_reference": "LBL-2026-1003",
                    "tracking_number": "TRK-2026-1003",
                    "cod_state": "Collected",
                    "payout_state": "Pending",
                    "return_state": "None",
                },
                adapter=speedy,
            )
        )
        self.assertIn(
            "tracking_number",
            shipment_validation_blockers(
                {
                    "shipment_id": "SHIP-2026-1004",
                    "order_id": "SO-2026-1004",
                    "courier_name": "Speedy",
                    "service_mode": "Address Delivery",
                    "destination_country": "BG",
                    "shipment_state": "Delivered",
                    "label_reference": "LBL-2026-1004",
                    "tracking_number": "",
                    "cod_state": "Pending",
                    "payout_state": "Pending",
                    "return_state": "None",
                },
                adapter=speedy,
            ),
        )
