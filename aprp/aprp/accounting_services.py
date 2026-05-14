"""APRP accounting service helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Protocol, runtime_checkable

from .purchasing_contract import (
    CashflowPlan,
    ProcurementProfile,
    PurchaseLiability,
    ReleaseForecast,
    build_monthly_accounting_summary,
)


def _clean_text(value: Any) -> str:
    """Return a stripped string representation for accounting fields."""

    if value is None:
        return ""
    return str(value).strip()


def _coerce_bool(value: Any) -> bool:
    """Return a stable boolean representation for accounting inputs."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _coerce_float(value: Any) -> float:
    """Return a float representation for accounting totals."""

    if value in {None, ""}:
        return 0.0
    return float(value)


def _mapping_from_input(value: Any) -> dict[str, Any]:
    """Return a mapping view for dict-like or dataclass inputs."""

    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"unsupported accounting input: {type(value)!r}")


def _normalize_supplier_vat_id(value: Any) -> str:
    """Return a canonical supplier VAT identifier."""

    return _clean_text(value).upper()


def _normalize_payment_state(value: Any) -> str:
    """Return a canonical payment-state label."""

    payment_state = _clean_text(value).title()
    return payment_state or "Unknown"


def _normalize_payment_method(value: Any) -> str:
    """Return a canonical payment-method label."""

    payment_method = _clean_text(value).upper().replace("-", "_")
    payment_method = payment_method.replace(" ", "_")
    return payment_method or "UNKNOWN"


def _normalize_release_forecast(
    value: Mapping[str, Any] | ReleaseForecast,
) -> ReleaseForecast:
    """Return a normalized release forecast contract row."""

    if isinstance(value, ReleaseForecast):
        return value
    forecast_data = _mapping_from_input(value)
    release_date = _clean_text(forecast_data.get("release_date")) or None
    order_date = _clean_text(forecast_data.get("order_date")) or None
    return ReleaseForecast(
        release_forecast_id=_clean_text(
            forecast_data.get("release_forecast_id")
        ),
        supplier_vat_id=_normalize_supplier_vat_id(
            forecast_data.get("supplier_vat_id")
        ),
        game=_clean_text(forecast_data.get("game")),
        release_name=_clean_text(forecast_data.get("release_name")),
        release_date=release_date,
        order_date=order_date,
        ordered_qty=_coerce_float(forecast_data.get("ordered_qty")),
        expected_fill_rate=_coerce_float(
            forecast_data.get("expected_fill_rate")
        ),
        forecast_demand_qty=_coerce_float(
            forecast_data.get("forecast_demand_qty")
        ),
        unit_cost_eur=_coerce_float(forecast_data.get("unit_cost_eur")),
        lead_time_days=int(forecast_data.get("lead_time_days") or 0),
        spoiler_signal_state=_clean_text(
            forecast_data.get("spoiler_signal_state")
        )
        or "Unknown",
        notes=_clean_text(forecast_data.get("notes")),
    )


def _normalize_procurement_profile(
    value: Mapping[str, Any] | ProcurementProfile,
) -> ProcurementProfile:
    """Return a normalized procurement profile contract row."""

    if isinstance(value, ProcurementProfile):
        return value
    profile_data = _mapping_from_input(value)
    forecasts = tuple(
        _normalize_release_forecast(forecast)
        for forecast in profile_data.get("release_forecasts", ())
    )
    return ProcurementProfile(
        profile_name=_clean_text(profile_data.get("profile_name")),
        supplier_vat_id=_normalize_supplier_vat_id(
            profile_data.get("supplier_vat_id")
        ),
        supplier_name=_clean_text(profile_data.get("supplier_name")),
        cash_budget_eur=_coerce_float(profile_data.get("cash_budget_eur")),
        salary_planning_eur=_coerce_float(
            profile_data.get("salary_planning_eur")
        ),
        release_forecasts=forecasts,
        notes=_clean_text(profile_data.get("notes")),
    )


def _normalize_purchase_liability(
    value: Mapping[str, Any] | PurchaseLiability,
) -> PurchaseLiability:
    """Return a normalized purchase-liability contract row."""

    if isinstance(value, PurchaseLiability):
        return value
    liability_data = _mapping_from_input(value)
    release_forecast_id = (
        _clean_text(liability_data.get("release_forecast_id")) or None
    )
    invoice_number = _clean_text(liability_data.get("invoice_number")) or None
    return PurchaseLiability(
        liability_id=_clean_text(liability_data.get("liability_id")),
        supplier_vat_id=_normalize_supplier_vat_id(
            liability_data.get("supplier_vat_id")
        ),
        expense_id=_clean_text(liability_data.get("expense_id")),
        release_forecast_id=release_forecast_id,
        invoice_number=invoice_number,
        ordered_qty=_coerce_float(liability_data.get("ordered_qty")),
        received_qty=_coerce_float(liability_data.get("received_qty")),
        forecast_liability_eur=_coerce_float(
            liability_data.get("forecast_liability_eur")
        ),
        invoice_amount_eur=_coerce_float(
            liability_data.get("invoice_amount_eur")
        ),
        landed_cost_eur=_coerce_float(liability_data.get("landed_cost_eur")),
        notes=_clean_text(liability_data.get("notes")),
    )


def _normalize_cashflow_plan(
    value: Mapping[str, Any] | CashflowPlan | None,
    *,
    period_name: str,
) -> CashflowPlan:
    """Return a normalized cashflow plan contract row."""

    if isinstance(value, CashflowPlan):
        return value
    plan_data = _mapping_from_input(value)
    return CashflowPlan(
        period_name=_clean_text(plan_data.get("period_name")) or period_name,
        opening_cash_eur=_coerce_float(plan_data.get("opening_cash_eur")),
        expected_inflow_eur=_coerce_float(
            plan_data.get("expected_inflow_eur")
        ),
        expected_purchase_outflow_eur=_coerce_float(
            plan_data.get("expected_purchase_outflow_eur")
        ),
        expected_salary_outflow_eur=_coerce_float(
            plan_data.get("expected_salary_outflow_eur")
        ),
        expected_landed_cost_eur=_coerce_float(
            plan_data.get("expected_landed_cost_eur")
        ),
        reserve_cash_eur=_coerce_float(plan_data.get("reserve_cash_eur")),
        notes=_clean_text(plan_data.get("notes")),
    )


def _normalize_sales_row(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a normalized sales export row."""

    row_data = _mapping_from_input(value)
    order_id = _clean_text(row_data.get("order_id"))
    payment_state = _normalize_payment_state(row_data.get("payment_state"))
    payment_method = _normalize_payment_method(row_data.get("payment_method"))
    gross_total_eur = _coerce_float(
        row_data.get("gross_total_eur")
        or row_data.get("grand_total_eur")
        or row_data.get("net_total_eur")
    )
    outstanding_amount_eur = _coerce_float(
        row_data.get("outstanding_amount_eur")
    )
    return {
        "order_id": order_id,
        "payment_state": payment_state,
        "payment_method": payment_method,
        "gross_total_eur": gross_total_eur,
        "outstanding_amount_eur": outstanding_amount_eur,
        "notes": _clean_text(row_data.get("notes")),
    }


def _normalize_settlement_row(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a normalized COD settlement row."""

    row_data = _mapping_from_input(value)
    settlement_id = _clean_text(row_data.get("settlement_id"))
    order_id = _clean_text(row_data.get("order_id"))
    status = _normalize_payment_state(row_data.get("status"))
    collected_total_eur = _coerce_float(
        row_data.get("collected_total_eur") or row_data.get("collected_eur")
    )
    due_total_eur = _coerce_float(row_data.get("due_total_eur"))
    payout_due_total_eur = _coerce_float(
        row_data.get("payout_due_total_eur") or row_data.get("payout_due_eur")
    )
    return {
        "settlement_id": settlement_id,
        "order_id": order_id,
        "status": status,
        "collected_total_eur": collected_total_eur,
        "due_total_eur": due_total_eur,
        "payout_due_total_eur": payout_due_total_eur,
        "notes": _clean_text(row_data.get("notes")),
    }


def _normalize_courier_row(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a normalized courier-fee row."""

    row_data = _mapping_from_input(value)
    courier_name = _clean_text(row_data.get("courier_name"))
    shipment_id = _clean_text(row_data.get("shipment_id"))
    fee_total_eur = _coerce_float(row_data.get("fee_total_eur"))
    cod_total_eur = _coerce_float(
        row_data.get("cod_total_eur") or row_data.get("cod_amount_eur")
    )
    payout_due_total_eur = _coerce_float(
        row_data.get("payout_due_total_eur") or row_data.get("payout_due_eur")
    )
    return {
        "courier_name": courier_name,
        "shipment_id": shipment_id,
        "fee_total_eur": fee_total_eur,
        "cod_total_eur": cod_total_eur,
        "payout_due_total_eur": payout_due_total_eur,
        "notes": _clean_text(row_data.get("notes")),
    }


@dataclass(frozen=True)
class PurchaseSummaryDraft:
    """Describe one operational purchase summary for APRP."""

    period_name: str
    supplier_count: int
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
    can_lock_period: bool
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this purchase summary."""

        return asdict(self)


@dataclass(frozen=True)
class SupplierLiabilitySummaryDraft:
    """Describe one supplier-liability review surface for APRP."""

    period_name: str
    supplier_count: int
    liability_count: int
    review_supplier_count: int
    supplier_rows: tuple[dict[str, Any], ...]
    invoice_total_eur: float
    landed_cost_total_eur: float
    variance_total_eur: float
    review_required: bool
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this liability summary."""

        return asdict(self)


@dataclass(frozen=True)
class SalesSummaryDraft:
    """Describe one sales summary grouped by payment state and method."""

    period_name: str
    order_count: int
    gross_total_eur: float
    outstanding_total_eur: float
    cod_order_count: int
    payment_state_rows: tuple[dict[str, Any], ...]
    payment_method_rows: tuple[dict[str, Any], ...]
    review_required: bool
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this sales summary."""

        return asdict(self)


@dataclass(frozen=True)
class CodSettlementSummaryDraft:
    """Describe one COD settlement summary for APRP."""

    period_name: str
    cod_order_count: int
    settlement_count: int
    collected_total_eur: float
    due_total_eur: float
    payout_due_total_eur: float
    settlement_rows: tuple[dict[str, Any], ...]
    review_required: bool
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this COD summary."""

        return asdict(self)


@dataclass(frozen=True)
class CourierFeeSummaryDraft:
    """Describe one courier-fee summary for APRP."""

    period_name: str
    courier_count: int
    shipment_count: int
    fee_total_eur: float
    cod_total_eur: float
    payout_due_total_eur: float
    courier_rows: tuple[dict[str, Any], ...]
    review_required: bool
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this courier summary."""

        return asdict(self)


@dataclass(frozen=True)
class AccountingExportPayloadDraft:
    """Describe one accountant-reviewable export payload for APRP."""

    period_name: str
    purchase_summary: PurchaseSummaryDraft
    supplier_liability_summary: SupplierLiabilitySummaryDraft
    sales_summary: SalesSummaryDraft
    cod_settlement_summary: CodSettlementSummaryDraft
    courier_fee_summary: CourierFeeSummaryDraft
    export_rows: tuple[dict[str, Any], ...]
    review_required: bool
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this export bundle."""

        return asdict(self)


@runtime_checkable
class AccountingAdapter(Protocol):
    """Describe the accounting service boundary used by APRP."""

    def build_purchase_summary_doc(
        self,
        period_name: str,
        procurement_profiles: Iterable[
            Mapping[str, Any] | ProcurementProfile
        ] = (),
        liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
        cashflow_plan: Mapping[str, Any] | CashflowPlan | None = None,
        notes: str = "",
    ) -> PurchaseSummaryDraft:
        """Build an operational purchase summary."""

    def build_supplier_liability_summary_doc(
        self,
        period_name: str,
        liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
        notes: str = "",
    ) -> SupplierLiabilitySummaryDraft:
        """Build a supplier-liability summary."""

    def build_sales_summary_doc(
        self,
        period_name: str,
        sales_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> SalesSummaryDraft:
        """Build a sales summary grouped by payment state."""

    def build_cod_settlement_summary_doc(
        self,
        period_name: str,
        sales_rows: Iterable[Mapping[str, Any]] = (),
        settlement_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> CodSettlementSummaryDraft:
        """Build a COD settlement summary."""

    def build_courier_fee_summary_doc(
        self,
        period_name: str,
        courier_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> CourierFeeSummaryDraft:
        """Build a courier-fee summary."""

    def build_accounting_export_payload_doc(
        self,
        period_name: str,
        procurement_profiles: Iterable[
            Mapping[str, Any] | ProcurementProfile
        ] = (),
        liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
        cashflow_plan: Mapping[str, Any] | CashflowPlan | None = None,
        sales_rows: Iterable[Mapping[str, Any]] = (),
        settlement_rows: Iterable[Mapping[str, Any]] = (),
        courier_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> AccountingExportPayloadDraft:
        """Build an accountant-reviewable export payload."""


def _group_rows(
    rows: Iterable[dict[str, Any]],
    *,
    key_name: str,
) -> tuple[dict[str, Any], ...]:
    """Return grouped summary rows with stable ordering."""

    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = _clean_text(row.get(key_name))
        bucket = grouped.setdefault(
            key,
            {
                key_name: key,
                "order_ids": (),
                "liability_ids": (),
                "shipment_ids": (),
                "settlement_ids": (),
                "count": 0,
                "total_eur": 0.0,
                "outstanding_total_eur": 0.0,
                "payout_due_total_eur": 0.0,
                "review_required": False,
            },
        )
        bucket["count"] = int(bucket["count"]) + 1
        bucket["review_required"] = bool(
            bucket["review_required"] or row.get("review_required")
        )
        if "order_id" in row and row["order_id"]:
            bucket["order_ids"] = bucket["order_ids"] + (row["order_id"],)
        if "liability_id" in row and row["liability_id"]:
            bucket["liability_ids"] = bucket["liability_ids"] + (
                row["liability_id"],
            )
        if "shipment_id" in row and row["shipment_id"]:
            bucket["shipment_ids"] = bucket["shipment_ids"] + (
                row["shipment_id"],
            )
        if "settlement_id" in row and row["settlement_id"]:
            bucket["settlement_ids"] = bucket["settlement_ids"] + (
                row["settlement_id"],
            )
        bucket["total_eur"] = round(
            float(bucket["total_eur"])
            + _coerce_float(
                row.get("gross_total_eur")
                or row.get("invoice_total_eur")
                or row.get("fee_total_eur")
                or row.get("collected_total_eur")
                or row.get("due_total_eur")
            ),
            2,
        )
        bucket["outstanding_total_eur"] = round(
            float(bucket["outstanding_total_eur"])
            + _coerce_float(row.get("outstanding_amount_eur")),
            2,
        )
        bucket["payout_due_total_eur"] = round(
            float(bucket["payout_due_total_eur"])
            + _coerce_float(row.get("payout_due_total_eur")),
            2,
        )
    return tuple(grouped[key] for key in sorted(grouped))


def _count_suppliers(
    procurement_profiles: Iterable[ProcurementProfile],
    liabilities: Iterable[PurchaseLiability],
) -> int:
    """Return the number of distinct suppliers in the purchase set."""

    supplier_ids = {
        profile.supplier_vat_id for profile in procurement_profiles
    }
    supplier_ids.update(
        liability.supplier_vat_id
        for liability in liabilities
        if liability.supplier_vat_id
    )
    return len(supplier_ids)


def build_purchase_summary_doc(
    period_name: str,
    procurement_profiles: Iterable[
        Mapping[str, Any] | ProcurementProfile
    ] = (),
    liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
    cashflow_plan: Mapping[str, Any] | CashflowPlan | None = None,
    notes: str = "",
) -> PurchaseSummaryDraft:
    """Build an operational purchase summary for one accounting period."""

    profile_rows = tuple(
        _normalize_procurement_profile(profile)
        for profile in procurement_profiles
    )
    liability_rows = tuple(
        _normalize_purchase_liability(liability) for liability in liabilities
    )
    plan = _normalize_cashflow_plan(cashflow_plan, period_name=period_name)
    summary = build_monthly_accounting_summary(
        period_name=period_name,
        procurement_profiles=profile_rows,
        liabilities=liability_rows,
        cashflow_plan=plan,
    )
    return PurchaseSummaryDraft(
        period_name=period_name,
        supplier_count=_count_suppliers(profile_rows, liability_rows),
        profile_count=summary.profile_count,
        release_forecast_count=summary.release_forecast_count,
        liability_count=summary.liability_count,
        procurement_commitment_eur=summary.procurement_commitment_eur,
        purchase_liability_total_eur=summary.purchase_liability_total_eur,
        liability_variance_total_eur=summary.liability_variance_total_eur,
        release_risk_total_eur=summary.release_risk_total_eur,
        salary_planning_total_eur=summary.salary_planning_total_eur,
        landed_cost_total_eur=summary.landed_cost_total_eur,
        expected_inflow_eur=summary.expected_inflow_eur,
        expected_outflow_eur=summary.expected_outflow_eur,
        opening_cash_eur=summary.opening_cash_eur,
        closing_cash_eur=summary.closing_cash_eur,
        reserve_cash_eur=summary.reserve_cash_eur,
        review_required=summary.review_required,
        can_lock_period=summary.can_lock_period(),
        notes=_clean_text(notes) or plan.notes,
    )


def build_supplier_liability_summary_doc(
    period_name: str,
    liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
    notes: str = "",
) -> SupplierLiabilitySummaryDraft:
    """Build a supplier-liability summary for one accounting period."""

    liability_rows = tuple(
        _normalize_purchase_liability(liability) for liability in liabilities
    )
    supplier_buckets: dict[str, list[PurchaseLiability]] = {}
    for liability in liability_rows:
        supplier_buckets.setdefault(liability.supplier_vat_id, []).append(
            liability
        )

    supplier_rows = []
    for supplier_vat_id in sorted(supplier_buckets):
        bucket = supplier_buckets[supplier_vat_id]
        supplier_rows.append(
            {
                "supplier_vat_id": supplier_vat_id,
                "liability_count": len(bucket),
                "liability_ids": tuple(
                    liability.liability_id for liability in bucket
                ),
                "invoice_total_eur": round(
                    sum(liability.invoice_amount_eur for liability in bucket),
                    2,
                ),
                "landed_cost_total_eur": round(
                    sum(liability.landed_cost_eur for liability in bucket),
                    2,
                ),
                "variance_total_eur": round(
                    sum(liability.variance_eur() for liability in bucket),
                    2,
                ),
                "review_required": any(
                    liability.needs_review() for liability in bucket
                ),
            }
        )

    review_required = any(row["review_required"] for row in supplier_rows)
    return SupplierLiabilitySummaryDraft(
        period_name=period_name,
        supplier_count=len(supplier_rows),
        liability_count=len(liability_rows),
        review_supplier_count=sum(
            1 for row in supplier_rows if row["review_required"]
        ),
        supplier_rows=tuple(supplier_rows),
        invoice_total_eur=round(
            sum(liability.invoice_amount_eur for liability in liability_rows),
            2,
        ),
        landed_cost_total_eur=round(
            sum(liability.landed_cost_eur for liability in liability_rows),
            2,
        ),
        variance_total_eur=round(
            sum(liability.variance_eur() for liability in liability_rows), 2
        ),
        review_required=review_required,
        notes=_clean_text(notes),
    )


def build_sales_summary_doc(
    period_name: str,
    sales_rows: Iterable[Mapping[str, Any]] = (),
    notes: str = "",
) -> SalesSummaryDraft:
    """Build a sales summary grouped by payment state and method."""

    normalized_rows = tuple(_normalize_sales_row(row) for row in sales_rows)
    state_buckets: dict[str, dict[str, Any]] = {}
    method_buckets: dict[str, dict[str, Any]] = {}
    gross_total_eur = 0.0
    outstanding_total_eur = 0.0
    cod_order_count = 0
    for row in normalized_rows:
        payment_state = row["payment_state"]
        payment_method = row["payment_method"]
        gross_total_eur = round(
            gross_total_eur + _coerce_float(row["gross_total_eur"]),
            2,
        )
        outstanding_total_eur = round(
            outstanding_total_eur
            + _coerce_float(row["outstanding_amount_eur"]),
            2,
        )
        if payment_method == "COD":
            cod_order_count += 1
        state_bucket = state_buckets.setdefault(
            payment_state,
            {
                "payment_state": payment_state,
                "order_count": 0,
                "order_ids": (),
                "gross_total_eur": 0.0,
                "outstanding_total_eur": 0.0,
                "review_required": False,
            },
        )
        state_bucket["order_count"] = int(state_bucket["order_count"]) + 1
        state_bucket["order_ids"] = state_bucket["order_ids"] + (
            row["order_id"],
        )
        state_bucket["gross_total_eur"] = round(
            float(state_bucket["gross_total_eur"]) + row["gross_total_eur"],
            2,
        )
        state_bucket["outstanding_total_eur"] = round(
            float(state_bucket["outstanding_total_eur"])
            + row["outstanding_amount_eur"],
            2,
        )
        if payment_state != "Paid" or row["outstanding_amount_eur"] > 0:
            state_bucket["review_required"] = True

        method_bucket = method_buckets.setdefault(
            payment_method,
            {
                "payment_method": payment_method,
                "order_count": 0,
                "order_ids": (),
                "gross_total_eur": 0.0,
                "outstanding_total_eur": 0.0,
                "review_required": False,
            },
        )
        method_bucket["order_count"] = int(method_bucket["order_count"]) + 1
        method_bucket["order_ids"] = method_bucket["order_ids"] + (
            row["order_id"],
        )
        method_bucket["gross_total_eur"] = round(
            float(method_bucket["gross_total_eur"]) + row["gross_total_eur"],
            2,
        )
        method_bucket["outstanding_total_eur"] = round(
            float(method_bucket["outstanding_total_eur"])
            + row["outstanding_amount_eur"],
            2,
        )
        if payment_method == "COD" or row["outstanding_amount_eur"] > 0:
            method_bucket["review_required"] = True

    payment_state_rows = tuple(
        state_buckets[key] for key in sorted(state_buckets)
    )
    payment_method_rows = tuple(
        method_buckets[key] for key in sorted(method_buckets)
    )
    review_required = bool(outstanding_total_eur > 0 or cod_order_count)
    return SalesSummaryDraft(
        period_name=period_name,
        order_count=len(normalized_rows),
        gross_total_eur=gross_total_eur,
        outstanding_total_eur=outstanding_total_eur,
        cod_order_count=cod_order_count,
        payment_state_rows=payment_state_rows,
        payment_method_rows=payment_method_rows,
        review_required=review_required,
        notes=_clean_text(notes),
    )


def build_cod_settlement_summary_doc(
    period_name: str,
    sales_rows: Iterable[Mapping[str, Any]] = (),
    settlement_rows: Iterable[Mapping[str, Any]] = (),
    notes: str = "",
) -> CodSettlementSummaryDraft:
    """Build a COD settlement summary from sales and settlement rows."""

    normalized_sales_rows = tuple(
        _normalize_sales_row(row) for row in sales_rows
    )
    cod_sales_rows = [
        row for row in normalized_sales_rows if row["payment_method"] == "COD"
    ]
    if settlement_rows:
        normalized_settlement_rows = tuple(
            _normalize_settlement_row(row) for row in settlement_rows
        )
    else:
        normalized_settlement_rows = tuple(
            {
                "settlement_id": row["order_id"],
                "order_id": row["order_id"],
                "status": (
                    "Pending" if row["outstanding_amount_eur"] else "Settled"
                ),
                "collected_total_eur": row["gross_total_eur"]
                - row["outstanding_amount_eur"],
                "due_total_eur": row["outstanding_amount_eur"],
                "payout_due_total_eur": row["outstanding_amount_eur"],
                "notes": "",
            }
            for row in cod_sales_rows
        )
    collected_total_eur = round(
        sum(row["collected_total_eur"] for row in normalized_settlement_rows),
        2,
    )
    due_total_eur = round(
        sum(row["due_total_eur"] for row in normalized_settlement_rows), 2
    )
    payout_due_total_eur = round(
        sum(row["payout_due_total_eur"] for row in normalized_settlement_rows),
        2,
    )
    settlement_rows_export = []
    for row in normalized_settlement_rows:
        settlement_rows_export.append(
            {
                "settlement_id": row["settlement_id"],
                "order_id": row["order_id"],
                "status": row["status"],
                "collected_total_eur": row["collected_total_eur"],
                "due_total_eur": row["due_total_eur"],
                "payout_due_total_eur": row["payout_due_total_eur"],
                "review_required": row["status"] != "Settled"
                or row["due_total_eur"] > 0,
            }
        )
    review_required = any(
        row["review_required"] for row in settlement_rows_export
    )
    return CodSettlementSummaryDraft(
        period_name=period_name,
        cod_order_count=len(cod_sales_rows),
        settlement_count=len(settlement_rows_export),
        collected_total_eur=collected_total_eur,
        due_total_eur=due_total_eur,
        payout_due_total_eur=payout_due_total_eur,
        settlement_rows=tuple(settlement_rows_export),
        review_required=review_required,
        notes=_clean_text(notes),
    )


def build_courier_fee_summary_doc(
    period_name: str,
    courier_rows: Iterable[Mapping[str, Any]] = (),
    notes: str = "",
) -> CourierFeeSummaryDraft:
    """Build a courier-fee summary from courier and shipment rows."""

    normalized_rows = tuple(
        _normalize_courier_row(row) for row in courier_rows
    )
    courier_buckets: dict[str, dict[str, Any]] = {}
    for row in normalized_rows:
        courier_name = _clean_text(row["courier_name"]) or "Unknown"
        bucket = courier_buckets.setdefault(
            courier_name,
            {
                "courier_name": courier_name,
                "shipment_count": 0,
                "shipment_ids": (),
                "fee_total_eur": 0.0,
                "cod_total_eur": 0.0,
                "payout_due_total_eur": 0.0,
                "review_required": False,
            },
        )
        bucket["shipment_count"] = int(bucket["shipment_count"]) + 1
        bucket["shipment_ids"] = bucket["shipment_ids"] + (row["shipment_id"],)
        bucket["fee_total_eur"] = round(
            float(bucket["fee_total_eur"]) + row["fee_total_eur"], 2
        )
        bucket["cod_total_eur"] = round(
            float(bucket["cod_total_eur"]) + row["cod_total_eur"], 2
        )
        bucket["payout_due_total_eur"] = round(
            float(bucket["payout_due_total_eur"])
            + row["payout_due_total_eur"],
            2,
        )
        if row["payout_due_total_eur"] > 0:
            bucket["review_required"] = True

    courier_rows_export = tuple(
        courier_buckets[key] for key in sorted(courier_buckets)
    )
    review_required = any(
        row["review_required"] for row in courier_rows_export
    )
    return CourierFeeSummaryDraft(
        period_name=period_name,
        courier_count=len(courier_rows_export),
        shipment_count=len(normalized_rows),
        fee_total_eur=round(
            sum(row["fee_total_eur"] for row in normalized_rows), 2
        ),
        cod_total_eur=round(
            sum(row["cod_total_eur"] for row in normalized_rows), 2
        ),
        payout_due_total_eur=round(
            sum(row["payout_due_total_eur"] for row in normalized_rows), 2
        ),
        courier_rows=courier_rows_export,
        review_required=review_required,
        notes=_clean_text(notes),
    )


def build_accounting_export_payload_doc(
    period_name: str,
    procurement_profiles: Iterable[
        Mapping[str, Any] | ProcurementProfile
    ] = (),
    liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
    cashflow_plan: Mapping[str, Any] | CashflowPlan | None = None,
    sales_rows: Iterable[Mapping[str, Any]] = (),
    settlement_rows: Iterable[Mapping[str, Any]] = (),
    courier_rows: Iterable[Mapping[str, Any]] = (),
    notes: str = "",
) -> AccountingExportPayloadDraft:
    """Build an accountant-reviewable export payload for APRP."""

    purchase_summary = build_purchase_summary_doc(
        period_name,
        procurement_profiles=procurement_profiles,
        liabilities=liabilities,
        cashflow_plan=cashflow_plan,
        notes=notes,
    )
    supplier_liability_summary = build_supplier_liability_summary_doc(
        period_name,
        liabilities=liabilities,
        notes=notes,
    )
    sales_summary = build_sales_summary_doc(
        period_name,
        sales_rows=sales_rows,
        notes=notes,
    )
    cod_settlement_summary = build_cod_settlement_summary_doc(
        period_name,
        sales_rows=sales_rows,
        settlement_rows=settlement_rows,
        notes=notes,
    )
    courier_fee_summary = build_courier_fee_summary_doc(
        period_name,
        courier_rows=courier_rows,
        notes=notes,
    )
    export_rows = (
        {
            "section": "purchase_summary",
            "payload": purchase_summary.to_doc(),
        },
        {
            "section": "supplier_liability_summary",
            "payload": supplier_liability_summary.to_doc(),
        },
        {
            "section": "sales_summary",
            "payload": sales_summary.to_doc(),
        },
        {
            "section": "cod_settlement_summary",
            "payload": cod_settlement_summary.to_doc(),
        },
        {
            "section": "courier_fee_summary",
            "payload": courier_fee_summary.to_doc(),
        },
    )
    review_required = any(
        (
            purchase_summary.review_required,
            supplier_liability_summary.review_required,
            sales_summary.review_required,
            cod_settlement_summary.review_required,
            courier_fee_summary.review_required,
        )
    )
    return AccountingExportPayloadDraft(
        period_name=period_name,
        purchase_summary=purchase_summary,
        supplier_liability_summary=supplier_liability_summary,
        sales_summary=sales_summary,
        cod_settlement_summary=cod_settlement_summary,
        courier_fee_summary=courier_fee_summary,
        export_rows=export_rows,
        review_required=review_required,
        notes=_clean_text(notes),
    )


class AccountingSimulatorAdapter:
    """Build proof-path accounting payloads without live credentials."""

    def sample_procurement_profiles(self) -> tuple[ProcurementProfile, ...]:
        """Return sample procurement profiles for the simulator."""

        return (
            ProcurementProfile(
                profile_name="Supplier BG123 May",
                supplier_vat_id="BG123",
                supplier_name="Sofia Supplier",
                cash_budget_eur=1200.0,
                salary_planning_eur=150.0,
                release_forecasts=(
                    ReleaseForecast(
                        release_forecast_id="RF-2026-0001",
                        supplier_vat_id="BG123",
                        game="APRP Launch",
                        release_name="Launch Pack",
                        release_date="2026-05-14",
                        order_date="2026-05-01",
                        ordered_qty=100,
                        expected_fill_rate=0.8,
                        forecast_demand_qty=60,
                        unit_cost_eur=2.5,
                        lead_time_days=14,
                        spoiler_signal_state="Hot",
                        notes="Demo procurement forecast",
                    ),
                ),
                notes="Primary supplier review",
            ),
            ProcurementProfile(
                profile_name="Supplier BG456 May",
                supplier_vat_id="BG456",
                supplier_name="Plovdiv Supplier",
                cash_budget_eur=900.0,
                salary_planning_eur=120.0,
                release_forecasts=(
                    ReleaseForecast(
                        release_forecast_id="RF-2026-0002",
                        supplier_vat_id="BG456",
                        game="APRP Support",
                        release_name="Support Pack",
                        release_date="2026-05-21",
                        order_date="2026-05-05",
                        ordered_qty=40,
                        expected_fill_rate=1.0,
                        forecast_demand_qty=35,
                        unit_cost_eur=4.0,
                        lead_time_days=10,
                        spoiler_signal_state="Review",
                        notes="Secondary supplier review",
                    ),
                ),
                notes="Backup supplier review",
            ),
        )

    def sample_liabilities(self) -> tuple[PurchaseLiability, ...]:
        """Return sample purchase liabilities for the simulator."""

        return (
            PurchaseLiability(
                liability_id="LIAB-2026-0001",
                supplier_vat_id="BG123",
                expense_id="EXP-2026-0001",
                release_forecast_id="RF-2026-0001",
                invoice_number="INV-001",
                ordered_qty=100,
                received_qty=96,
                forecast_liability_eur=200.0,
                invoice_amount_eur=212.0,
                landed_cost_eur=12.0,
                notes="Variance under review",
            ),
            PurchaseLiability(
                liability_id="LIAB-2026-0002",
                supplier_vat_id="BG456",
                expense_id="EXP-2026-0002",
                release_forecast_id="RF-2026-0002",
                invoice_number="INV-002",
                ordered_qty=40,
                received_qty=40,
                forecast_liability_eur=160.0,
                invoice_amount_eur=160.0,
                landed_cost_eur=8.0,
                notes="Matched invoice",
            ),
        )

    def sample_sales_rows(self) -> tuple[dict[str, Any], ...]:
        """Return sample sales rows for the simulator."""

        return (
            {
                "order_id": "SO-2026-1001",
                "payment_state": "Paid",
                "payment_method": "COD",
                "gross_total_eur": 95.0,
                "outstanding_amount_eur": 0.0,
                "notes": "Delivered COD order",
            },
            {
                "order_id": "SO-2026-1002",
                "payment_state": "Pending",
                "payment_method": "Bank Transfer",
                "gross_total_eur": 120.0,
                "outstanding_amount_eur": 120.0,
                "notes": "Awaiting transfer",
            },
            {
                "order_id": "SO-2026-1003",
                "payment_state": "Returned",
                "payment_method": "Cash",
                "gross_total_eur": 30.0,
                "outstanding_amount_eur": 0.0,
                "notes": "Returned line",
            },
            {
                "order_id": "SO-2026-1004",
                "payment_state": "Paid",
                "payment_method": "COD",
                "gross_total_eur": 60.0,
                "outstanding_amount_eur": 0.0,
                "notes": "Second COD order",
            },
        )

    def sample_settlement_rows(self) -> tuple[dict[str, Any], ...]:
        """Return sample COD settlement rows for the simulator."""

        return (
            {
                "settlement_id": "SET-2026-0001",
                "order_id": "SO-2026-1001",
                "status": "Settled",
                "collected_total_eur": 95.0,
                "due_total_eur": 0.0,
                "payout_due_total_eur": 4.5,
                "notes": "Collected by courier",
            },
            {
                "settlement_id": "SET-2026-0002",
                "order_id": "SO-2026-1004",
                "status": "Pending",
                "collected_total_eur": 0.0,
                "due_total_eur": 60.0,
                "payout_due_total_eur": 3.0,
                "notes": "Awaiting payout",
            },
        )

    def sample_courier_rows(self) -> tuple[dict[str, Any], ...]:
        """Return sample courier-fee rows for the simulator."""

        return (
            {
                "courier_name": "Speedy",
                "shipment_id": "SHIP-2026-0001",
                "fee_total_eur": 8.5,
                "cod_total_eur": 155.0,
                "payout_due_total_eur": 3.5,
                "notes": "Primary line",
            },
            {
                "courier_name": "Econt",
                "shipment_id": "SHIP-2026-0002",
                "fee_total_eur": 6.0,
                "cod_total_eur": 0.0,
                "payout_due_total_eur": 0.0,
                "notes": "Secondary line",
            },
        )

    def build_purchase_summary_doc(
        self,
        period_name: str,
        procurement_profiles: Iterable[
            Mapping[str, Any] | ProcurementProfile
        ] = (),
        liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
        cashflow_plan: Mapping[str, Any] | CashflowPlan | None = None,
        notes: str = "",
    ) -> PurchaseSummaryDraft:
        """Build a purchase summary using the module helper."""

        return build_purchase_summary_doc(
            period_name,
            procurement_profiles=procurement_profiles,
            liabilities=liabilities,
            cashflow_plan=cashflow_plan,
            notes=notes,
        )

    def build_supplier_liability_summary_doc(
        self,
        period_name: str,
        liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
        notes: str = "",
    ) -> SupplierLiabilitySummaryDraft:
        """Build a supplier-liability summary using the module helper."""

        return build_supplier_liability_summary_doc(
            period_name,
            liabilities=liabilities,
            notes=notes,
        )

    def build_sales_summary_doc(
        self,
        period_name: str,
        sales_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> SalesSummaryDraft:
        """Build a sales summary using the module helper."""

        return build_sales_summary_doc(
            period_name,
            sales_rows=sales_rows,
            notes=notes,
        )

    def build_cod_settlement_summary_doc(
        self,
        period_name: str,
        sales_rows: Iterable[Mapping[str, Any]] = (),
        settlement_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> CodSettlementSummaryDraft:
        """Build a COD settlement summary using the module helper."""

        return build_cod_settlement_summary_doc(
            period_name,
            sales_rows=sales_rows,
            settlement_rows=settlement_rows,
            notes=notes,
        )

    def build_courier_fee_summary_doc(
        self,
        period_name: str,
        courier_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> CourierFeeSummaryDraft:
        """Build a courier-fee summary using the module helper."""

        return build_courier_fee_summary_doc(
            period_name,
            courier_rows=courier_rows,
            notes=notes,
        )

    def build_accounting_export_payload_doc(
        self,
        period_name: str,
        procurement_profiles: Iterable[
            Mapping[str, Any] | ProcurementProfile
        ] = (),
        liabilities: Iterable[Mapping[str, Any] | PurchaseLiability] = (),
        cashflow_plan: Mapping[str, Any] | CashflowPlan | None = None,
        sales_rows: Iterable[Mapping[str, Any]] = (),
        settlement_rows: Iterable[Mapping[str, Any]] = (),
        courier_rows: Iterable[Mapping[str, Any]] = (),
        notes: str = "",
    ) -> AccountingExportPayloadDraft:
        """Build an accountant-reviewable export payload."""

        return build_accounting_export_payload_doc(
            period_name,
            procurement_profiles=procurement_profiles,
            liabilities=liabilities,
            cashflow_plan=cashflow_plan,
            sales_rows=sales_rows,
            settlement_rows=settlement_rows,
            courier_rows=courier_rows,
            notes=notes,
        )


__all__ = [
    "AccountingAdapter",
    "AccountingExportPayloadDraft",
    "AccountingSimulatorAdapter",
    "CodSettlementSummaryDraft",
    "CourierFeeSummaryDraft",
    "PurchaseSummaryDraft",
    "SalesSummaryDraft",
    "SupplierLiabilitySummaryDraft",
    "build_accounting_export_payload_doc",
    "build_cod_settlement_summary_doc",
    "build_courier_fee_summary_doc",
    "build_purchase_summary_doc",
    "build_sales_summary_doc",
    "build_supplier_liability_summary_doc",
]
