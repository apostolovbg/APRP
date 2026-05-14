"""Accounting service helper tests for APRP."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import aprp.aprp as package
from aprp.aprp import (
    AccountingAdapter,
    AccountingExportPayloadDraft,
    AccountingSimulatorAdapter,
    CodSettlementSummaryDraft,
    CourierFeeSummaryDraft,
    PurchaseSummaryDraft,
    SalesSummaryDraft,
    SupplierLiabilitySummaryDraft,
    build_accounting_export_payload_doc,
    build_cod_settlement_summary_doc,
    build_courier_fee_summary_doc,
    build_purchase_summary_doc,
    build_sales_summary_doc,
    build_supplier_liability_summary_doc,
)


class TestAprpAccountingServices(unittest.TestCase):
    """Verify the accounting service layer stays explicit."""

    def test_package_exports_accounting_service_helpers(self):
        """Ensure the package exposes the accounting service layer."""

        module = importlib.import_module("aprp.aprp.accounting_services")
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")
        docs = Path("docs/accounting.md").read_text(encoding="utf-8")

        self.assertIn("APRP", module.__doc__ or "")
        self.assertIn("aprp.aprp.accounting_services", readme)
        self.assertIn("aprp.aprp.accounting_services", spec)
        self.assertIn("aprp.aprp.accounting_services", docs)
        self.assertIs(package.AccountingAdapter, AccountingAdapter)
        self.assertIs(
            package.AccountingExportPayloadDraft,
            AccountingExportPayloadDraft,
        )
        self.assertIs(
            package.AccountingSimulatorAdapter,
            AccountingSimulatorAdapter,
        )
        self.assertIs(
            package.CodSettlementSummaryDraft,
            CodSettlementSummaryDraft,
        )
        self.assertIs(package.CourierFeeSummaryDraft, CourierFeeSummaryDraft)
        self.assertIs(package.PurchaseSummaryDraft, PurchaseSummaryDraft)
        self.assertIs(package.SalesSummaryDraft, SalesSummaryDraft)
        self.assertIs(
            package.SupplierLiabilitySummaryDraft,
            SupplierLiabilitySummaryDraft,
        )
        self.assertIs(
            package.build_accounting_export_payload_doc,
            build_accounting_export_payload_doc,
        )
        self.assertIs(
            package.build_cod_settlement_summary_doc,
            build_cod_settlement_summary_doc,
        )
        self.assertIs(
            package.build_courier_fee_summary_doc,
            build_courier_fee_summary_doc,
        )
        self.assertIs(
            package.build_purchase_summary_doc,
            build_purchase_summary_doc,
        )
        self.assertIs(
            package.build_sales_summary_doc,
            build_sales_summary_doc,
        )
        self.assertIs(
            package.build_supplier_liability_summary_doc,
            build_supplier_liability_summary_doc,
        )
        self.assertEqual(AccountingAdapter.__name__, "AccountingAdapter")
        self.assertEqual(
            AccountingAdapter.build_purchase_summary_doc.__name__,
            "build_purchase_summary_doc",
        )
        self.assertEqual(
            AccountingAdapter.build_supplier_liability_summary_doc.__name__,
            "build_supplier_liability_summary_doc",
        )
        self.assertEqual(
            AccountingAdapter.build_sales_summary_doc.__name__,
            "build_sales_summary_doc",
        )
        self.assertEqual(
            AccountingAdapter.build_cod_settlement_summary_doc.__name__,
            "build_cod_settlement_summary_doc",
        )
        self.assertEqual(
            AccountingAdapter.build_courier_fee_summary_doc.__name__,
            "build_courier_fee_summary_doc",
        )
        self.assertEqual(
            AccountingAdapter.build_accounting_export_payload_doc.__name__,
            "build_accounting_export_payload_doc",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.__name__,
            "AccountingSimulatorAdapter",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.sample_procurement_profiles.__name__,
            "sample_procurement_profiles",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.sample_liabilities.__name__,
            "sample_liabilities",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.sample_sales_rows.__name__,
            "sample_sales_rows",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.sample_settlement_rows.__name__,
            "sample_settlement_rows",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.sample_courier_rows.__name__,
            "sample_courier_rows",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.build_purchase_summary_doc.__name__,
            "build_purchase_summary_doc",
        )
        self.assertEqual(
            AccountingSimulatorAdapter.build_sales_summary_doc.__name__,
            "build_sales_summary_doc",
        )
        self.assertEqual(
            getattr(
                AccountingSimulatorAdapter,
                "build_accounting_export_payload_doc",
            ).__name__,
            "build_accounting_export_payload_doc",
        )
        self.assertTrue(callable(build_accounting_export_payload_doc))
        self.assertTrue(callable(build_cod_settlement_summary_doc))
        self.assertTrue(callable(build_courier_fee_summary_doc))
        self.assertTrue(callable(build_purchase_summary_doc))
        self.assertTrue(callable(build_sales_summary_doc))
        self.assertTrue(callable(build_supplier_liability_summary_doc))
        self.assertEqual(PurchaseSummaryDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            SupplierLiabilitySummaryDraft.to_doc.__name__,
            "to_doc",
        )
        self.assertEqual(SalesSummaryDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            CodSettlementSummaryDraft.to_doc.__name__,
            "to_doc",
        )
        self.assertEqual(CourierFeeSummaryDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            AccountingExportPayloadDraft.to_doc.__name__,
            "to_doc",
        )

    def test_simulator_adapter_builds_summaries_and_export_payload(self):
        """Ensure the simulator adapter builds accountant-review data."""

        simulator = AccountingSimulatorAdapter()
        procurement_profiles = simulator.sample_procurement_profiles()
        liabilities = simulator.sample_liabilities()
        sales_rows = simulator.sample_sales_rows()
        settlement_rows = simulator.sample_settlement_rows()
        courier_rows = simulator.sample_courier_rows()
        purchase_summary = simulator.build_purchase_summary_doc(
            "2026-05",
            procurement_profiles=procurement_profiles,
            liabilities=liabilities,
            cashflow_plan={
                "opening_cash_eur": 1000.0,
                "expected_inflow_eur": 3000.0,
                "expected_purchase_outflow_eur": 1000.0,
                "expected_salary_outflow_eur": 400.0,
                "expected_landed_cost_eur": 20.0,
                "reserve_cash_eur": 500.0,
            },
            notes="Accounting proof run",
        )
        supplier_summary = simulator.build_supplier_liability_summary_doc(
            "2026-05",
            liabilities=liabilities,
            notes="Accounting proof run",
        )
        sales_summary = simulator.build_sales_summary_doc(
            "2026-05",
            sales_rows=sales_rows,
            notes="Accounting proof run",
        )
        cod_summary = simulator.build_cod_settlement_summary_doc(
            "2026-05",
            sales_rows=sales_rows,
            settlement_rows=settlement_rows,
            notes="Accounting proof run",
        )
        courier_summary = simulator.build_courier_fee_summary_doc(
            "2026-05",
            courier_rows=courier_rows,
            notes="Accounting proof run",
        )
        export_payload = simulator.build_accounting_export_payload_doc(
            "2026-05",
            procurement_profiles=procurement_profiles,
            liabilities=liabilities,
            cashflow_plan={
                "opening_cash_eur": 1000.0,
                "expected_inflow_eur": 3000.0,
                "expected_purchase_outflow_eur": 1000.0,
                "expected_salary_outflow_eur": 400.0,
                "expected_landed_cost_eur": 20.0,
                "reserve_cash_eur": 500.0,
            },
            sales_rows=sales_rows,
            settlement_rows=settlement_rows,
            courier_rows=courier_rows,
            notes="Accounting proof run",
        )

        self.assertIsInstance(simulator, AccountingAdapter)
        self.assertEqual(2, purchase_summary.supplier_count)
        self.assertEqual(2, purchase_summary.profile_count)
        self.assertEqual(2, purchase_summary.release_forecast_count)
        self.assertEqual(2, purchase_summary.liability_count)
        self.assertEqual(360.0, purchase_summary.procurement_commitment_eur)
        self.assertEqual(372.0, purchase_summary.purchase_liability_total_eur)
        self.assertEqual(12.0, purchase_summary.liability_variance_total_eur)
        self.assertEqual(479.0, purchase_summary.release_risk_total_eur)
        self.assertEqual(270.0, purchase_summary.salary_planning_total_eur)
        self.assertEqual(20.0, purchase_summary.landed_cost_total_eur)
        self.assertEqual(3000.0, purchase_summary.expected_inflow_eur)
        self.assertEqual(1420.0, purchase_summary.expected_outflow_eur)
        self.assertEqual(1000.0, purchase_summary.opening_cash_eur)
        self.assertEqual(2580.0, purchase_summary.closing_cash_eur)
        self.assertEqual(500.0, purchase_summary.reserve_cash_eur)
        self.assertTrue(purchase_summary.review_required)
        self.assertFalse(purchase_summary.can_lock_period)
        self.assertEqual("Accounting proof run", purchase_summary.notes)
        self.assertEqual(2, supplier_summary.supplier_count)
        self.assertEqual(2, supplier_summary.liability_count)
        self.assertEqual(1, supplier_summary.review_supplier_count)
        self.assertEqual(2, len(supplier_summary.supplier_rows))
        self.assertEqual(
            "BG123",
            supplier_summary.supplier_rows[0]["supplier_vat_id"],
        )
        self.assertEqual(
            212.0,
            supplier_summary.supplier_rows[0]["invoice_total_eur"],
        )
        self.assertEqual(
            160.0,
            supplier_summary.supplier_rows[1]["invoice_total_eur"],
        )
        self.assertEqual(372.0, supplier_summary.invoice_total_eur)
        self.assertEqual(20.0, supplier_summary.landed_cost_total_eur)
        self.assertEqual(12.0, supplier_summary.variance_total_eur)
        self.assertTrue(supplier_summary.review_required)
        self.assertEqual(4, sales_summary.order_count)
        self.assertEqual(305.0, sales_summary.gross_total_eur)
        self.assertEqual(120.0, sales_summary.outstanding_total_eur)
        self.assertEqual(2, sales_summary.cod_order_count)
        self.assertEqual(3, len(sales_summary.payment_state_rows))
        self.assertEqual(
            "Paid",
            sales_summary.payment_state_rows[0]["payment_state"],
        )
        self.assertEqual(
            "Pending",
            sales_summary.payment_state_rows[1]["payment_state"],
        )
        self.assertEqual(
            "BANK_TRANSFER",
            sales_summary.payment_method_rows[0]["payment_method"],
        )
        self.assertEqual(
            "COD",
            sales_summary.payment_method_rows[2]["payment_method"],
        )
        self.assertTrue(sales_summary.review_required)
        self.assertEqual(2, cod_summary.cod_order_count)
        self.assertEqual(2, cod_summary.settlement_count)
        self.assertEqual(95.0, cod_summary.collected_total_eur)
        self.assertEqual(60.0, cod_summary.due_total_eur)
        self.assertEqual(7.5, cod_summary.payout_due_total_eur)
        self.assertEqual("Settled", cod_summary.settlement_rows[0]["status"])
        self.assertEqual("Pending", cod_summary.settlement_rows[1]["status"])
        self.assertTrue(cod_summary.review_required)
        self.assertEqual(2, courier_summary.courier_count)
        self.assertEqual(2, courier_summary.shipment_count)
        self.assertEqual(14.5, courier_summary.fee_total_eur)
        self.assertEqual(155.0, courier_summary.cod_total_eur)
        self.assertEqual(3.5, courier_summary.payout_due_total_eur)
        self.assertEqual(
            "Econt",
            courier_summary.courier_rows[0]["courier_name"],
        )
        self.assertEqual(
            "Speedy",
            courier_summary.courier_rows[1]["courier_name"],
        )
        self.assertTrue(courier_summary.review_required)
        self.assertTrue(export_payload.review_required)
        self.assertEqual(5, len(export_payload.export_rows))
        self.assertEqual(
            "purchase_summary",
            export_payload.export_rows[0]["section"],
        )
        self.assertEqual(
            "courier_fee_summary",
            export_payload.export_rows[4]["section"],
        )
        self.assertEqual(
            "Accounting proof run",
            export_payload.notes,
        )
