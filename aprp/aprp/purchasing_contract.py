"""Core APRP procurement, release, and accounting contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ReleaseForecast:
    """Describe one release-specific procurement forecast."""

    release_forecast_id: str
    supplier_vat_id: str
    game: str
    release_name: str
    release_date: str | None = None
    order_date: str | None = None
    ordered_qty: float = 0.0
    expected_fill_rate: float = 0.5
    forecast_demand_qty: float = 0.0
    unit_cost_eur: float = 0.0
    lead_time_days: int = 0
    spoiler_signal_state: str = "Unknown"
    notes: str = ""

    def stream_key(self) -> str:
        """Return the stable procurement stream key."""

        return "|".join(
            [
                self.supplier_vat_id.strip(),
                self.game.strip(),
                self.release_name.strip(),
            ]
        )

    def expected_received_qty(self) -> float:
        """Return the expected received quantity from the fill rate."""

        return round(self.ordered_qty * self.expected_fill_rate, 4)

    def expected_sell_through_qty(self) -> float:
        """Return the expected sell-through quantity."""

        return min(self.expected_received_qty(), self.forecast_demand_qty)

    def expected_excess_qty(self) -> float:
        """Return the expected excess quantity after demand is met."""

        return max(
            self.expected_received_qty() - self.forecast_demand_qty, 0.0
        )

    def expected_payment_eur(self) -> float:
        """Return the expected cash exposure for the forecast."""

        return round(self.expected_received_qty() * self.unit_cost_eur, 2)

    def cash_risk_eur(self) -> float:
        """Return the cash at risk if demand underperforms."""

        excess_risk = self.expected_excess_qty() * self.unit_cost_eur
        return round(self.expected_payment_eur() + excess_risk, 2)

    def risk_score(self) -> float:
        """Return a simple risk score for procurement review."""

        return round(
            self.cash_risk_eur()
            + self.expected_excess_qty()
            + float(self.lead_time_days),
            2,
        )

    def needs_override(self) -> bool:
        """Return whether the forecast needs an explicit override."""

        signal = self.spoiler_signal_state.strip().lower()
        recommended_qty = max(
            self.forecast_demand_qty,
            self.expected_received_qty(),
        )
        if signal == "overbought":
            return True
        return self.ordered_qty > recommended_qty * 1.25

    def recommendation_state(self) -> str:
        """Return the procurement recommendation for the forecast."""

        signal = self.spoiler_signal_state.strip().lower()
        if self.needs_override():
            return "Review"
        if signal == "hot":
            return "Buy"
        if signal in {"cold", "overbought"}:
            return "Hold"
        if self.expected_excess_qty() == 0:
            return "Buy"
        return "Review"


@dataclass(frozen=True)
class ProcurementProfile:
    """Describe one supplier-facing procurement profile."""

    profile_name: str
    supplier_vat_id: str
    supplier_name: str = ""
    cash_budget_eur: float = 0.0
    salary_planning_eur: float = 0.0
    release_forecasts: tuple[ReleaseForecast, ...] = ()
    notes: str = ""

    def release_forecast_ids(self) -> tuple[str, ...]:
        """Return the tracked forecast identifiers."""

        return tuple(
            forecast.release_forecast_id for forecast in self.release_forecasts
        )

    def expected_purchase_commitment_eur(self) -> float:
        """Return the expected purchase commitment for the profile."""

        return round(
            sum(
                forecast.expected_payment_eur()
                for forecast in self.release_forecasts
            ),
            2,
        )

    def release_risk_eur(self) -> float:
        """Return the combined release risk score for the profile."""

        return round(
            sum(forecast.risk_score() for forecast in self.release_forecasts),
            2,
        )

    def cashflow_pressure_eur(self) -> float:
        """Return the cash pressure before liabilities settle."""

        return round(
            self.expected_purchase_commitment_eur() + self.salary_planning_eur,
            2,
        )

    def needs_review(self) -> bool:
        """Return whether the profile needs explicit review."""

        if (
            self.cash_budget_eur
            and self.cashflow_pressure_eur() > self.cash_budget_eur
        ):
            return True
        return any(
            forecast.needs_override() for forecast in self.release_forecasts
        )


@dataclass(frozen=True)
class PurchaseLiability:
    """Describe one supplier liability and its accounting variance."""

    liability_id: str
    supplier_vat_id: str
    expense_id: str
    release_forecast_id: str | None = None
    invoice_number: str | None = None
    ordered_qty: float = 0.0
    received_qty: float = 0.0
    forecast_liability_eur: float = 0.0
    invoice_amount_eur: float = 0.0
    landed_cost_eur: float = 0.0
    notes: str = ""

    def variance_eur(self) -> float:
        """Return the invoice variance against the forecast liability."""

        return round(self.invoice_amount_eur - self.forecast_liability_eur, 2)

    def total_commitment_eur(self) -> float:
        """Return the full commitment including landed cost."""

        return round(self.invoice_amount_eur + self.landed_cost_eur, 2)

    def needs_review(self) -> bool:
        """Return whether the liability needs accounting review."""

        if self.received_qty > self.ordered_qty:
            return True
        return abs(self.variance_eur()) > 0.01


@dataclass(frozen=True)
class CashflowPlan:
    """Describe one monthly cashflow plan."""

    period_name: str
    opening_cash_eur: float = 0.0
    expected_inflow_eur: float = 0.0
    expected_purchase_outflow_eur: float = 0.0
    expected_salary_outflow_eur: float = 0.0
    expected_landed_cost_eur: float = 0.0
    reserve_cash_eur: float = 0.0
    notes: str = ""

    def total_outflow_eur(self) -> float:
        """Return the planned cash outflow."""

        return round(
            self.expected_purchase_outflow_eur
            + self.expected_salary_outflow_eur
            + self.expected_landed_cost_eur,
            2,
        )

    def net_cashflow_eur(self) -> float:
        """Return the planned net cashflow."""

        return round(self.expected_inflow_eur - self.total_outflow_eur(), 2)

    def closing_cash_eur(self) -> float:
        """Return the planned closing cash balance."""

        return round(self.opening_cash_eur + self.net_cashflow_eur(), 2)

    def liquidity_gap_eur(self) -> float:
        """Return the shortfall against the reserve cash target."""

        return max(self.reserve_cash_eur - self.closing_cash_eur(), 0.0)

    def is_safe(self) -> bool:
        """Return whether the plan keeps the reserve target covered."""

        return self.closing_cash_eur() >= self.reserve_cash_eur


@dataclass(frozen=True)
class AccountingSummary:
    """Describe one accountant-ready monthly summary."""

    period_name: str
    profile_count: int
    release_forecast_count: int
    liability_count: int
    procurement_commitment_eur: float
    purchase_liability_total_eur: float
    liability_variance_total_eur: float
    release_risk_total_eur: float
    salary_planning_total_eur: float
    landed_cost_total_eur: float
    expected_inflow_eur: float
    expected_outflow_eur: float
    opening_cash_eur: float
    closing_cash_eur: float
    reserve_cash_eur: float
    review_required: bool

    def can_lock_period(self) -> bool:
        """Return whether the period can be lock-checked."""

        return (
            not self.review_required
            and self.closing_cash_eur >= self.reserve_cash_eur
        )


def build_monthly_accounting_summary(
    period_name: str,
    procurement_profiles: Iterable[ProcurementProfile],
    liabilities: Iterable[PurchaseLiability],
    cashflow_plan: CashflowPlan,
) -> AccountingSummary:
    """Build a monthly accounting summary from the shared procurement data."""

    profile_rows = tuple(procurement_profiles)
    liability_rows = tuple(liabilities)
    procurement_commitment_eur = round(
        sum(
            profile.expected_purchase_commitment_eur()
            for profile in profile_rows
        ),
        2,
    )
    purchase_liability_total_eur = round(
        sum(liability.invoice_amount_eur for liability in liability_rows),
        2,
    )
    liability_variance_total_eur = round(
        sum(liability.variance_eur() for liability in liability_rows),
        2,
    )
    release_risk_total_eur = round(
        sum(profile.release_risk_eur() for profile in profile_rows),
        2,
    )
    salary_planning_total_eur = round(
        sum(profile.salary_planning_eur for profile in profile_rows),
        2,
    )
    landed_cost_total_eur = round(
        sum(liability.landed_cost_eur for liability in liability_rows),
        2,
    )
    review_required = (
        any(profile.needs_review() for profile in profile_rows)
        or any(liability.needs_review() for liability in liability_rows)
        or not cashflow_plan.is_safe()
    )
    return AccountingSummary(
        period_name=period_name,
        profile_count=len(profile_rows),
        release_forecast_count=sum(
            len(profile.release_forecasts) for profile in profile_rows
        ),
        liability_count=len(liability_rows),
        procurement_commitment_eur=procurement_commitment_eur,
        purchase_liability_total_eur=purchase_liability_total_eur,
        liability_variance_total_eur=liability_variance_total_eur,
        release_risk_total_eur=release_risk_total_eur,
        salary_planning_total_eur=salary_planning_total_eur,
        landed_cost_total_eur=landed_cost_total_eur,
        expected_inflow_eur=cashflow_plan.expected_inflow_eur,
        expected_outflow_eur=cashflow_plan.total_outflow_eur(),
        opening_cash_eur=cashflow_plan.opening_cash_eur,
        closing_cash_eur=cashflow_plan.closing_cash_eur(),
        reserve_cash_eur=cashflow_plan.reserve_cash_eur,
        review_required=review_required,
    )


__all__ = [
    "AccountingSummary",
    "CashflowPlan",
    "ProcurementProfile",
    "PurchaseLiability",
    "ReleaseForecast",
    "build_monthly_accounting_summary",
]
