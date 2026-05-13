"""Core APRP purchasing and accounting contract tests."""

import unittest
from pathlib import Path

from aprp.aprp import (
    AccountingSummary,
    CashflowPlan,
    ProcurementProfile,
    PurchaseLiability,
    ReleaseForecast,
    build_monthly_accounting_summary,
)


class TestAprpPurchasingContract(unittest.TestCase):
    """Verify procurement, release, and accounting hooks stay explicit."""

    def test_release_forecasts_keep_release_risk_reviewable(self):
        """Ensure release forecasts turn signals into cash and review data."""
        forecast = ReleaseForecast(
            release_forecast_id="RF-2026-0001",
            supplier_vat_id="BG123456789",
            game="APRP Demo Title",
            release_name="Launch Batch",
            release_date="2026-06-01",
            order_date="2026-05-13",
            ordered_qty=10,
            expected_fill_rate=0.8,
            forecast_demand_qty=6,
            unit_cost_eur=12.5,
            lead_time_days=14,
            spoiler_signal_state="Hot",
        )
        review_forecast = ReleaseForecast(
            release_forecast_id="RF-2026-0002",
            supplier_vat_id="BG123456789",
            game="APRP Demo Title",
            release_name="Reserve Batch",
            ordered_qty=20,
            expected_fill_rate=0.5,
            forecast_demand_qty=4,
            unit_cost_eur=12.5,
            lead_time_days=21,
            spoiler_signal_state="Overbought",
        )

        self.assertEqual(
            "BG123456789|APRP Demo Title|Launch Batch",
            forecast.stream_key(),
        )
        self.assertEqual(8.0, forecast.expected_received_qty())
        self.assertEqual(6.0, forecast.expected_sell_through_qty())
        self.assertEqual(2.0, forecast.expected_excess_qty())
        self.assertEqual(100.0, forecast.expected_payment_eur())
        self.assertEqual(125.0, forecast.cash_risk_eur())
        self.assertEqual(141.0, forecast.risk_score())
        self.assertFalse(forecast.needs_override())
        self.assertEqual("Buy", forecast.recommendation_state())

        self.assertTrue(review_forecast.needs_override())
        self.assertEqual("Review", review_forecast.recommendation_state())

    def test_procurement_profiles_keep_budget_pressure_explicit(self):
        """Ensure procurement profiles aggregate release and budget data."""
        forecast = ReleaseForecast(
            release_forecast_id="RF-2026-0001",
            supplier_vat_id="BG123456789",
            game="APRP Demo Title",
            release_name="Launch Batch",
            ordered_qty=10,
            expected_fill_rate=0.8,
            forecast_demand_qty=6,
            unit_cost_eur=12.5,
            lead_time_days=14,
            spoiler_signal_state="Hot",
        )
        profile = ProcurementProfile(
            profile_name="Supplier Alpha",
            supplier_vat_id="BG123456789",
            supplier_name="Supplier Alpha Ltd",
            cash_budget_eur=150.0,
            salary_planning_eur=40.0,
            release_forecasts=(forecast,),
        )
        review_profile = ProcurementProfile(
            profile_name="Supplier Beta",
            supplier_vat_id="BG987654321",
            cash_budget_eur=120.0,
            salary_planning_eur=40.0,
            release_forecasts=(forecast,),
        )

        self.assertEqual(("RF-2026-0001",), profile.release_forecast_ids())
        self.assertEqual(100.0, profile.expected_purchase_commitment_eur())
        self.assertEqual(141.0, profile.release_risk_eur())
        self.assertEqual(140.0, profile.cashflow_pressure_eur())
        self.assertFalse(profile.needs_review())
        self.assertTrue(review_profile.needs_review())

    def test_liabilities_and_cashflow_plans_keep_review_data_visible(self):
        """Ensure liabilities and cashflow plans stay explicit."""
        liability = PurchaseLiability(
            liability_id="LIAB-2026-0001",
            supplier_vat_id="BG123456789",
            expense_id="EXP-2026-0001",
            release_forecast_id="RF-2026-0001",
            invoice_number="INV-2026-0001",
            ordered_qty=10,
            received_qty=12,
            forecast_liability_eur=100.0,
            invoice_amount_eur=105.5,
            landed_cost_eur=6.5,
        )
        plan = CashflowPlan(
            period_name="2026-05",
            opening_cash_eur=200.0,
            expected_inflow_eur=150.0,
            expected_purchase_outflow_eur=80.0,
            expected_salary_outflow_eur=40.0,
            expected_landed_cost_eur=10.0,
            reserve_cash_eur=100.0,
        )

        self.assertEqual(5.5, liability.variance_eur())
        self.assertEqual(112.0, liability.total_commitment_eur())
        self.assertTrue(liability.needs_review())
        self.assertEqual(130.0, plan.total_outflow_eur())
        self.assertEqual(20.0, plan.net_cashflow_eur())
        self.assertEqual(220.0, plan.closing_cash_eur())
        self.assertEqual(0.0, plan.liquidity_gap_eur())
        self.assertTrue(plan.is_safe())

    def test_monthly_summary_rolls_up_procurement_and_accounting_data(self):
        """Ensure the monthly summary consumes the same source data."""
        forecast = ReleaseForecast(
            release_forecast_id="RF-2026-0001",
            supplier_vat_id="BG123456789",
            game="APRP Demo Title",
            release_name="Launch Batch",
            ordered_qty=10,
            expected_fill_rate=0.8,
            forecast_demand_qty=6,
            unit_cost_eur=12.5,
            lead_time_days=14,
            spoiler_signal_state="Hot",
        )
        profile = ProcurementProfile(
            profile_name="Supplier Alpha",
            supplier_vat_id="BG123456789",
            cash_budget_eur=150.0,
            salary_planning_eur=40.0,
            release_forecasts=(forecast,),
        )
        liability = PurchaseLiability(
            liability_id="LIAB-2026-0001",
            supplier_vat_id="BG123456789",
            expense_id="EXP-2026-0001",
            release_forecast_id="RF-2026-0001",
            invoice_number="INV-2026-0001",
            ordered_qty=10,
            received_qty=12,
            forecast_liability_eur=100.0,
            invoice_amount_eur=105.5,
            landed_cost_eur=6.5,
        )
        plan = CashflowPlan(
            period_name="2026-05",
            opening_cash_eur=200.0,
            expected_inflow_eur=150.0,
            expected_purchase_outflow_eur=80.0,
            expected_salary_outflow_eur=40.0,
            expected_landed_cost_eur=10.0,
            reserve_cash_eur=100.0,
        )

        summary = build_monthly_accounting_summary(
            "2026-05",
            (profile,),
            (liability,),
            plan,
        )

        self.assertIsInstance(summary, AccountingSummary)
        self.assertEqual(1, summary.profile_count)
        self.assertEqual(1, summary.release_forecast_count)
        self.assertEqual(1, summary.liability_count)
        self.assertEqual(100.0, summary.procurement_commitment_eur)
        self.assertEqual(105.5, summary.purchase_liability_total_eur)
        self.assertEqual(5.5, summary.liability_variance_total_eur)
        self.assertEqual(141.0, summary.release_risk_total_eur)
        self.assertEqual(40.0, summary.salary_planning_total_eur)
        self.assertEqual(6.5, summary.landed_cost_total_eur)
        self.assertEqual(150.0, summary.expected_inflow_eur)
        self.assertEqual(130.0, summary.expected_outflow_eur)
        self.assertEqual(200.0, summary.opening_cash_eur)
        self.assertEqual(220.0, summary.closing_cash_eur)
        self.assertEqual(100.0, summary.reserve_cash_eur)
        self.assertTrue(summary.review_required)
        self.assertFalse(summary.can_lock_period())

    def test_contract_symbols_stay_explicit(self):
        """Ensure the exported purchasing symbols stay named directly."""
        self.assertEqual(ReleaseForecast.__name__, "ReleaseForecast")
        self.assertEqual(ProcurementProfile.__name__, "ProcurementProfile")
        self.assertEqual(PurchaseLiability.__name__, "PurchaseLiability")
        self.assertEqual(CashflowPlan.__name__, "CashflowPlan")
        self.assertEqual(
            build_monthly_accounting_summary.__name__,
            "build_monthly_accounting_summary",
        )

    def test_purchasing_docs_cover_the_accounting_contract(self):
        """Ensure the purchasing guides mention the accounting contract."""
        purchasing = Path("docs/purchasing.md").read_text(encoding="utf-8")
        accounting = Path("docs/accounting.md").read_text(encoding="utf-8")

        for token in [
            "aprp.aprp.purchasing_contract",
            "Release Forecast",
            "Procurement Profile",
            "Purchase Liability",
            "Cashflow Plan",
            "Accounting Summary",
        ]:
            self.assertIn(token, purchasing)

        for token in [
            "Release Forecast",
            "Purchase Liability",
            "Cashflow Plan",
            "Accounting Summary",
            "period lock",
        ]:
            self.assertIn(token, accounting)
