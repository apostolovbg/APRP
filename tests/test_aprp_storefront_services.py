"""Storefront service helper tests for APRP."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import aprp.aprp as package
from aprp.aprp import (
    StorefrontAdapter,
    StorefrontAvailabilitySyncPayload,
    StorefrontProductSyncPayload,
    StorefrontSimulatorAdapter,
    StorefrontStockSyncPayload,
    StorefrontSyncBatchDraft,
    StorefrontSyncEventDraft,
    StorefrontWooCommerceAdapter,
)


class TestAprpStorefrontServices(unittest.TestCase):
    """Verify the storefront service layer stays explicit."""

    def test_package_exports_storefront_service_helpers(self):
        """Ensure the package exposes the storefront service layer."""

        module = importlib.import_module("aprp.aprp.storefront_services")
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")
        docs = Path("docs/storefront.md").read_text(encoding="utf-8")

        self.assertIn("APRP", module.__doc__ or "")
        self.assertIn("aprp.aprp.storefront_services", readme)
        self.assertIn("aprp.aprp.storefront_services", spec)
        self.assertIn("aprp.aprp.storefront_services", docs)
        self.assertIs(package.StorefrontAdapter, StorefrontAdapter)
        self.assertIs(
            package.StorefrontAvailabilitySyncPayload,
            StorefrontAvailabilitySyncPayload,
        )
        self.assertIs(
            package.StorefrontProductSyncPayload,
            StorefrontProductSyncPayload,
        )
        self.assertIs(
            package.StorefrontSimulatorAdapter,
            StorefrontSimulatorAdapter,
        )
        self.assertIs(
            package.StorefrontStockSyncPayload,
            StorefrontStockSyncPayload,
        )
        self.assertIs(
            package.StorefrontSyncBatchDraft,
            StorefrontSyncBatchDraft,
        )
        self.assertIs(
            package.StorefrontSyncEventDraft,
            StorefrontSyncEventDraft,
        )
        self.assertIs(
            package.StorefrontWooCommerceAdapter,
            StorefrontWooCommerceAdapter,
        )
        self.assertEqual(
            module.EVENT_TYPES,
            ("Catalog", "Order", "Reservation", "Refund", "Customer"),
        )
        self.assertEqual(
            module.SYNC_STATUSES,
            ("Pending", "Synced", "Failed"),
        )
        self.assertEqual(
            module.BATCH_STATUSES,
            ("Draft", "In Progress", "Synced", "Failed"),
        )
        self.assertEqual(StorefrontAdapter.__name__, "StorefrontAdapter")
        self.assertEqual(
            StorefrontProductSyncPayload.__name__,
            "StorefrontProductSyncPayload",
        )
        self.assertEqual(
            StorefrontStockSyncPayload.__name__,
            "StorefrontStockSyncPayload",
        )
        self.assertEqual(
            StorefrontAvailabilitySyncPayload.__name__,
            "StorefrontAvailabilitySyncPayload",
        )
        self.assertEqual(
            StorefrontSyncEventDraft.__name__,
            "StorefrontSyncEventDraft",
        )
        self.assertEqual(
            StorefrontSyncBatchDraft.__name__,
            "StorefrontSyncBatchDraft",
        )
        self.assertEqual(
            StorefrontSimulatorAdapter.__name__,
            "StorefrontSimulatorAdapter",
        )
        self.assertEqual(
            StorefrontWooCommerceAdapter.__name__,
            "StorefrontWooCommerceAdapter",
        )

    def test_simulator_adapter_builds_payloads_and_batch_drafts(self):
        """Ensure the simulator adapter builds the proof-path payloads."""

        simulator = StorefrontSimulatorAdapter(storefront_host="aprp.store")
        rows = simulator.sample_catalog_rows()
        product_payloads = simulator.build_product_sync_payloads(rows)
        stock_payloads = simulator.build_stock_sync_payloads(rows)
        availability_payloads = simulator.build_availability_sync_payloads(
            rows
        )
        order = simulator.ingest_order(
            {
                "order_id": "SO-2026-1001",
                "storefront_host": "aprp.store",
                "customer_ref": "WEB-2026-1001",
                "currency": "EUR",
                "order_state": "Submitted",
                "payment_state": "Pending",
                "https_only": True,
                "source_language": "bg",
                "order_lines": [
                    {
                        "item_code": "APRP-ITEM-001",
                        "sku": "SKU-001",
                        "item_name": "APRP Starter Box",
                        "quantity": 1,
                        "unit_price_eur": 19.9,
                        "warehouse": "Sofia - Fulfillment",
                    }
                ],
            }
        )
        batch = simulator.build_sync_batch(
            batch_id="SYNC-2026-0001",
            catalog_rows=rows,
            order_rows=(order,),
            started_on="2026-05-13 10:00:00",
            finished_on="2026-05-13 10:05:00",
            notes="Storefront proof run",
        )

        self.assertIsInstance(simulator, StorefrontAdapter)
        self.assertEqual(2, len(rows))
        self.assertEqual(1, len(product_payloads))
        self.assertEqual(2, len(stock_payloads))
        self.assertEqual(2, len(availability_payloads))
        self.assertEqual("SKU-001", product_payloads[0].sku)
        self.assertTrue(product_payloads[0].publishable)
        self.assertEqual(10.0, stock_payloads[0].available_quantity)
        self.assertFalse(availability_payloads[1].publishable)
        self.assertEqual("SO-2026-1001", order.order_id)
        self.assertEqual(1, order.line_count())
        self.assertTrue(order.https_only)
        self.assertFalse(order.needs_review())
        self.assertEqual(2, batch.catalog_rows)
        self.assertEqual(1, batch.order_rows)
        self.assertEqual("Failed", batch.status)
        self.assertEqual(3, len(batch.events))
        self.assertEqual("Synced", batch.events[0].sync_status)
        self.assertEqual("Failed", batch.events[1].sync_status)
        self.assertEqual("Synced", batch.events[2].sync_status)
        self.assertEqual("Blocked from publication", batch.events[1].notes)
        self.assertEqual("aprp.store", batch.storefront_host)

    def test_woocommerce_adapter_normalizes_https_order_boundary(self):
        """Ensure the WooCommerce shell keeps the HTTPS boundary explicit."""

        adapter = StorefrontWooCommerceAdapter(
            storefront_host="aprp.store",
            api_base_url="https://kuche.aprp.store/wp-json/wc/v3",
            consumer_key="ck_test",
            consumer_secret="cs_test",
        )
        order = adapter.ingest_order(
            {
                "order_id": "SO-2026-1002",
                "storefront_host": "aprp.store",
                "customer_ref": "WEB-2026-1002",
                "currency": "BGN",
                "order_state": "Submitted",
                "payment_state": "Pending",
                "https_only": False,
                "source_language": "bg",
                "order_lines": [
                    {
                        "item_code": "APRP-ITEM-001",
                        "sku": "SKU-001",
                        "item_name": "APRP Starter Box",
                        "quantity": 1,
                        "unit_price_eur": 19.9,
                        "warehouse": "Sofia - Fulfillment",
                    }
                ],
            }
        )

        self.assertIsInstance(adapter, StorefrontAdapter)
        self.assertEqual("WooCommerce", adapter.adapter_name)
        self.assertEqual(
            "https://kuche.aprp.store/wp-json/wc/v3",
            adapter.api_base_url,
        )
        self.assertEqual("SO-2026-1002", order.order_id)
        self.assertFalse(order.https_only)
        self.assertTrue(order.needs_review())
        self.assertEqual(1, order.line_count())
        self.assertEqual(19.9, order.gross_total_eur())
        self.assertTrue(order.requires_erp_reservation())

    def test_storefront_payload_and_batch_drafts_map_to_doctypes(self):
        """Ensure the draft payloads stay DocType-shaped."""

        product_payload = StorefrontProductSyncPayload(
            sku="SKU-001",
            name="APRP Starter Box",
            description="Sample storefront product",
            price_eur=19.9,
            stock_qty=12,
            visible_stock_qty=10,
            publication_state="Publish",
            availability_state="Available",
            backorders_allowed=False,
            tax_class="Standard",
            shipping_class="Box",
            language="bg",
            publishable=True,
            notes="Sample storefront product",
            web_buffer_qty=2,
        )
        stock_payload = StorefrontStockSyncPayload(
            sku="SKU-001",
            warehouse="APRP-ITEM-001",
            raw_quantity=12,
            available_quantity=10,
            web_buffer_qty=2,
            backorders_allowed=False,
            pack_family="Starter",
            notes="Sample stock payload",
        )
        availability_payload = StorefrontAvailabilitySyncPayload(
            sku="SKU-001",
            publication_state="Publish",
            availability_state="Available",
            available_quantity=10,
            backorders_allowed=False,
            publishable=True,
            notes="Sample availability payload",
        )
        event = StorefrontSyncEventDraft(
            event_type="Catalog",
            source_ref="SKU-001",
            product_profile="APRP Starter Box",
            sync_status="Synced",
            notes="Sample storefront event",
        )
        batch = StorefrontSyncBatchDraft(
            batch_id="SYNC-2026-1001",
            storefront_host="aprp.store",
            status="Synced",
            started_on="2026-05-13 10:00:00",
            finished_on="2026-05-13 10:05:00",
            catalog_rows=2,
            order_rows=1,
            notes="Sample storefront batch",
            events=(event,),
        )

        self.assertEqual("SKU-001", product_payload.to_doc()["sku"])
        self.assertEqual("APRP-ITEM-001", stock_payload.to_doc()["warehouse"])
        self.assertEqual(
            "Available",
            availability_payload.to_doc()["availability_state"],
        )
        self.assertEqual("Catalog", event.to_doc()["event_type"])
        self.assertEqual("SYNC-2026-1001", batch.to_doc()["batch_id"])
        self.assertEqual(1, len(batch.to_doc()["events"]))
        self.assertEqual("Synced", batch.to_doc()["events"][0]["sync_status"])
        self.assertEqual(2, batch.to_doc()["catalog_rows"])
        self.assertEqual(1, batch.to_doc()["order_rows"])

    def test_storefront_service_class_methods_cover_symbol_paths(self):
        """Ensure the storefront service methods stay explicit."""

        self.assertEqual(
            StorefrontSimulatorAdapter.sample_catalog_rows.__name__,
            "sample_catalog_rows",
        )
        self.assertEqual(
            StorefrontSimulatorAdapter.build_product_sync_payloads.__name__,
            "build_product_sync_payloads",
        )
        self.assertEqual(
            StorefrontSimulatorAdapter.build_stock_sync_payloads.__name__,
            "build_stock_sync_payloads",
        )
        self.assertEqual(
            getattr(
                StorefrontSimulatorAdapter.build_availability_sync_payloads,
                "__name__",
            ),
            "build_availability_sync_payloads",
        )
        self.assertEqual(
            StorefrontSimulatorAdapter.build_sync_event.__name__,
            "build_sync_event",
        )
        self.assertEqual(
            StorefrontSimulatorAdapter.build_sync_batch.__name__,
            "build_sync_batch",
        )
        self.assertEqual(
            StorefrontSimulatorAdapter.ingest_order.__name__,
            "ingest_order",
        )
        self.assertEqual(
            StorefrontWooCommerceAdapter.ingest_order.__name__,
            "ingest_order",
        )
