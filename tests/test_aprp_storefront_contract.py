"""Core APRP storefront contract tests."""

import unittest
from pathlib import Path

from aprp.aprp import (
    StorefrontCatalogRow,
    StorefrontOrder,
    StorefrontOrderLine,
    StorefrontReservation,
    StorefrontSyncBatch,
    StorefrontSyncSummary,
    build_storefront_sync_summary,
)


class TestAprpStorefrontContract(unittest.TestCase):
    """Verify the blind storefront and order-flow model stays explicit."""

    def test_storefront_catalog_rows_keep_public_state_explicit(self):
        """Ensure catalog rows keep ERP truth and visible stock together."""
        row = StorefrontCatalogRow(
            item_code="APRP-ITEM-001",
            sku="SKU-001",
            item_name="APRP Starter Box",
            price_eur=19.9,
            stock_qty=12,
            web_buffer_qty=2,
            publication_state="Publish",
            availability_state="Available",
        )
        hidden_row = StorefrontCatalogRow(
            item_code="APRP-ITEM-002",
            sku="SKU-002",
            item_name="APRP Hidden Box",
            price_eur=25.0,
            stock_qty=6,
            publication_state="Hidden",
            availability_state="Available",
        )

        self.assertEqual("SKU-001", row.storefront_key())
        self.assertEqual(10.0, row.visible_stock_qty())
        self.assertTrue(row.is_publishable())
        self.assertFalse(row.needs_review())
        self.assertFalse(hidden_row.is_publishable())
        self.assertTrue(hidden_row.needs_review())

    def test_storefront_orders_and_reservations_keep_order_flow_explicit(
        self,
    ):
        """Ensure storefront orders flow back into ERP reservation data."""
        line = StorefrontOrderLine(
            item_code="APRP-ITEM-001",
            sku="SKU-001",
            item_name="APRP Starter Box",
            quantity=2,
            unit_price_eur=19.9,
            warehouse="Sofia - Fulfillment",
        )
        order = StorefrontOrder(
            order_id="SO-2026-0001",
            storefront_host="aprp.store",
            customer_ref="WEB-2026-0001",
            order_state="Submitted",
            payment_state="Pending",
            order_lines=(line,),
        )
        reservation = StorefrontReservation(
            reservation_id="RES-2026-0001",
            order_id="SO-2026-0001",
            item_code="APRP-ITEM-001",
            sku="SKU-001",
            warehouse="Sofia - Fulfillment",
            quantity=2,
            reservation_state="Reserved",
        )

        self.assertEqual(39.8, line.line_total_eur())
        self.assertTrue(line.requires_reservation())
        self.assertEqual(1, order.line_count())
        self.assertEqual(39.8, order.gross_total_eur())
        self.assertTrue(order.requires_erp_reservation())
        self.assertFalse(order.needs_review())
        self.assertTrue(reservation.is_active())
        self.assertFalse(reservation.needs_review())

    def test_storefront_sync_summary_rolls_up_public_and_erp_state(self):
        """Ensure the sync batch turns storefront state into one summary."""
        publishable_row = StorefrontCatalogRow(
            item_code="APRP-ITEM-001",
            sku="SKU-001",
            item_name="APRP Starter Box",
            price_eur=19.9,
            stock_qty=12,
            web_buffer_qty=2,
            publication_state="Publish",
            availability_state="Available",
        )
        review_row = StorefrontCatalogRow(
            item_code="APRP-ITEM-002",
            sku="SKU-002",
            item_name="APRP Hidden Box",
            price_eur=25.0,
            stock_qty=6,
            publication_state="Hidden",
            availability_state="Available",
        )
        order = StorefrontOrder(
            order_id="SO-2026-0001",
            storefront_host="aprp.store",
            customer_ref="WEB-2026-0001",
            order_state="Submitted",
            payment_state="Pending",
            order_lines=(
                StorefrontOrderLine(
                    item_code="APRP-ITEM-001",
                    sku="SKU-001",
                    item_name="APRP Starter Box",
                    quantity=2,
                    unit_price_eur=19.9,
                ),
            ),
        )
        reservation = StorefrontReservation(
            reservation_id="RES-2026-0001",
            order_id="SO-2026-0001",
            item_code="APRP-ITEM-001",
            sku="SKU-001",
            warehouse="Sofia - Fulfillment",
            quantity=2,
            reservation_state="Reserved",
        )
        batch = StorefrontSyncBatch(
            batch_id="SYNC-2026-0001",
            storefront_host="aprp.store",
            catalog_rows=(publishable_row, review_row),
            orders=(order,),
            reservations=(reservation,),
        )

        summary = build_storefront_sync_summary(batch)

        self.assertIsInstance(summary, StorefrontSyncSummary)
        self.assertEqual(2, summary.catalog_count)
        self.assertEqual(1, summary.publishable_count)
        self.assertEqual(1, summary.order_count)
        self.assertEqual(1, summary.reservation_count)
        self.assertEqual(10.0, summary.visible_stock_qty)
        self.assertEqual(39.8, summary.gross_order_total_eur)
        self.assertTrue(summary.https_only)
        self.assertTrue(summary.review_required)
        self.assertFalse(summary.is_ready_to_sync())
        self.assertEqual((publishable_row,), batch.publishable_rows())

    def test_storefront_docs_cover_the_sync_contract(self):
        """Ensure the storefront guide names the sync contract directly."""
        storefront = Path("docs/storefront.md").read_text(encoding="utf-8")

        for token in [
            "aprp.aprp.storefront_contract",
            "Storefront Catalog Row",
            "Storefront Order",
            "Storefront Reservation",
            "Storefront Sync Summary",
            "HTTPS",
        ]:
            self.assertIn(token, storefront)

    def test_contract_symbols_stay_explicit(self):
        """Ensure the exported storefront symbols stay named directly."""
        self.assertEqual(StorefrontCatalogRow.__name__, "StorefrontCatalogRow")
        self.assertEqual(StorefrontOrderLine.__name__, "StorefrontOrderLine")
        self.assertEqual(StorefrontOrder.__name__, "StorefrontOrder")
        self.assertEqual(
            StorefrontReservation.__name__,
            "StorefrontReservation",
        )
        self.assertEqual(StorefrontSyncBatch.__name__, "StorefrontSyncBatch")
        self.assertEqual(
            StorefrontSyncSummary.__name__,
            "StorefrontSyncSummary",
        )
        self.assertEqual(
            build_storefront_sync_summary.__name__,
            "build_storefront_sync_summary",
        )
