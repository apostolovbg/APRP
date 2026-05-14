"""APRP safe showcase service helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any

from .storefront_contract import (
    StorefrontCatalogRow,
    StorefrontOrder,
    StorefrontOrderLine,
)
from .storefront_services import StorefrontSimulatorAdapter

SHOWCASE_SESSION_COOKIE_NAME = "aprp_showcase_session"
SHOWCASE_CONTROLLED_ACTIONS = (
    "Browse the seeded storefront catalog",
    "Place a disposable showcase checkout",
    "Reset the showcase session",
    "Reseed demo-only records",
)
SHOWCASE_SCREENSHARE_CHECKLIST = (
    "Start from a fresh disposable session.",
    "Show HTTPS-only public entrypoints.",
    "Demonstrate the seeded catalog and checkout flow.",
    "Keep ERP admin surfaces hidden.",
    "Reset the showcase state before ending the session.",
)
SHOWCASE_PUBLIC_DEMO_CHECKLIST = (
    "Confirm HTTPS is enabled on the public entrypoint.",
    "Confirm anonymous visitors stay on storefront surfaces.",
    "Confirm the session cookie is disposable and resettable.",
    "Confirm demo-only records are separated from production records.",
    "Confirm the reset path clears demo state without touching prod.",
)
SHOWCASE_RESET_STEPS = (
    "Clear the disposable session cookie and browser state.",
    "Remove demo-only records.",
    "Restore the seeded showcase rows.",
    "Verify production rows were untouched.",
)


def _clean_text(value: Any) -> str:
    """Return a stripped string representation for showcase fields."""

    if value is None:
        return ""
    return str(value).strip()


def _mapping_from_input(value: Any) -> dict[str, Any]:
    """Return a mapping view for dict-like or dataclass inputs."""

    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"unsupported showcase input: {type(value)!r}")


def _coerce_float(value: Any) -> float:
    """Return a float representation for showcase quantities."""

    if value in {None, ""}:
        return 0.0
    return float(value)


def _coerce_bool(value: Any) -> bool:
    """Return a stable boolean representation for showcase inputs."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _normalize_catalog_row(
    value: Mapping[str, Any] | StorefrontCatalogRow,
) -> StorefrontCatalogRow:
    """Return a normalized storefront catalog row for showcase seed data."""

    catalog_data = _mapping_from_input(value)
    item_name = _clean_text(catalog_data.get("item_name"))
    if not item_name:
        item_name = _clean_text(catalog_data.get("name"))
    return StorefrontCatalogRow(
        item_code=_clean_text(catalog_data.get("item_code")),
        sku=_clean_text(catalog_data.get("sku")),
        item_name=item_name,
        price_eur=_coerce_float(catalog_data.get("price_eur")),
        stock_qty=_coerce_float(catalog_data.get("stock_qty")),
        web_buffer_qty=_coerce_float(catalog_data.get("web_buffer_qty")),
        publication_state=_clean_text(catalog_data.get("publication_state"))
        or "Hidden",
        availability_state=_clean_text(catalog_data.get("availability_state"))
        or "Unknown",
        backorders_allowed=_coerce_bool(
            catalog_data.get("backorders_allowed")
        ),
        tax_class=_clean_text(catalog_data.get("tax_class")),
        shipping_class=_clean_text(catalog_data.get("shipping_class")),
        language=_clean_text(catalog_data.get("language")) or "bg",
        notes=_clean_text(catalog_data.get("notes")),
    )


def _normalize_order_line(
    value: Mapping[str, Any] | StorefrontOrderLine,
) -> StorefrontOrderLine:
    """Return a normalized storefront order line."""

    line_data = _mapping_from_input(value)
    return StorefrontOrderLine(
        item_code=_clean_text(line_data.get("item_code")),
        sku=_clean_text(line_data.get("sku")),
        item_name=_clean_text(line_data.get("item_name")),
        quantity=_coerce_float(line_data.get("quantity")),
        unit_price_eur=_coerce_float(line_data.get("unit_price_eur")),
        tax_rate=_coerce_float(line_data.get("tax_rate")),
        warehouse=_clean_text(line_data.get("warehouse")),
        reservation_state=_clean_text(line_data.get("reservation_state"))
        or "Pending",
        notes=_clean_text(line_data.get("notes")),
    )


def _normalize_order(
    value: Mapping[str, Any] | StorefrontOrder,
    *,
    public_host: str,
    session_cookie_name: str,
) -> StorefrontOrder:
    """Return a normalized storefront order for showcase seed data."""

    order_data = _mapping_from_input(value)
    normalized_lines = tuple(
        _normalize_order_line(order_line)
        for order_line in order_data.get("order_lines", ())
    )
    order_id = _clean_text(order_data.get("order_id"))
    storefront_host = _clean_text(
        order_data.get("storefront_host")
    ) or _clean_text(public_host)
    customer_ref = _clean_text(order_data.get("customer_ref"))
    if not order_id:
        raise ValueError("order_id is required")
    if not storefront_host:
        raise ValueError("storefront_host is required")
    if not customer_ref:
        raise ValueError("customer_ref is required")
    if not normalized_lines:
        raise ValueError("order_lines are required")
    return StorefrontOrder(
        order_id=order_id,
        storefront_host=storefront_host,
        customer_ref=customer_ref,
        currency=_clean_text(order_data.get("currency")) or "EUR",
        order_state=_clean_text(order_data.get("order_state")) or "Pending",
        payment_state=_clean_text(order_data.get("payment_state"))
        or "Pending",
        https_only=(
            _coerce_bool(order_data.get("https_only"))
            if "https_only" in order_data
            else True
        ),
        public_session_id=_clean_text(order_data.get("public_session_id"))
        or f"{session_cookie_name}:disposable",
        source_language=_clean_text(order_data.get("source_language")) or "bg",
        order_lines=normalized_lines,
        notes=_clean_text(order_data.get("notes")),
    )


def _build_demo_order(
    public_host: str,
    session_cookie_name: str,
    disposable_session_label: str,
    catalog_rows: tuple[StorefrontCatalogRow, ...],
) -> StorefrontOrder:
    """Return one disposable showcase order from the seed catalog."""

    simulator = StorefrontSimulatorAdapter(storefront_host=public_host)
    source_row = next(
        (row for row in catalog_rows if row.is_publishable()),
        catalog_rows[0],
    )
    return simulator.ingest_order(
        {
            "order_id": "SHOWCASE-ORDER-001",
            "storefront_host": public_host,
            "customer_ref": "SHOWCASE-CUSTOMER-001",
            "currency": "EUR",
            "order_state": "Submitted",
            "payment_state": "Pending",
            "https_only": True,
            "public_session_id": f"{session_cookie_name}:disposable",
            "source_language": "bg",
            "order_lines": [
                {
                    "item_code": source_row.item_code,
                    "sku": source_row.sku,
                    "item_name": source_row.item_name,
                    "quantity": 1,
                    "unit_price_eur": source_row.price_eur,
                    "warehouse": source_row.item_code,
                }
            ],
            "notes": disposable_session_label,
        }
    )


@dataclass(frozen=True)
class ShowcaseDemoRecord:
    """Describe one showcase-only record marker."""

    record_type: str
    record_ref: str
    demo_only: bool = True
    resettable: bool = True
    session_scope: str = "Disposable"
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the marker as a plain dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class ShowcaseSeedPlan:
    """Describe one safe showcase seed plan."""

    public_host: str
    backend_host: str
    session_cookie_name: str
    disposable_session_label: str
    catalog_rows: tuple[StorefrontCatalogRow, ...]
    order_rows: tuple[StorefrontOrder, ...]
    demo_records: tuple[ShowcaseDemoRecord, ...]
    controlled_actions: tuple[str, ...] = SHOWCASE_CONTROLLED_ACTIONS
    reset_steps: tuple[str, ...] = SHOWCASE_RESET_STEPS
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the seed plan as a plain dictionary."""

        return {
            "public_host": self.public_host,
            "backend_host": self.backend_host,
            "session_cookie_name": self.session_cookie_name,
            "disposable_session_label": self.disposable_session_label,
            "catalog_rows": [asdict(row) for row in self.catalog_rows],
            "order_rows": [asdict(order) for order in self.order_rows],
            "demo_records": [record.to_doc() for record in self.demo_records],
            "controlled_actions": list(self.controlled_actions),
            "reset_steps": list(self.reset_steps),
            "notes": self.notes,
        }

    def demo_record_refs(self) -> tuple[str, ...]:
        """Return the record refs tagged as showcase-only."""

        return tuple(record.record_ref for record in self.demo_records)


@dataclass(frozen=True)
class ShowcaseResetPlan:
    """Describe one safe showcase reset plan."""

    public_host: str
    backend_host: str
    session_cookie_name: str
    disposable_session_label: str
    demo_records: tuple[ShowcaseDemoRecord, ...]
    reset_steps: tuple[str, ...] = SHOWCASE_RESET_STEPS
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the reset plan as a plain dictionary."""

        return {
            "public_host": self.public_host,
            "backend_host": self.backend_host,
            "session_cookie_name": self.session_cookie_name,
            "disposable_session_label": self.disposable_session_label,
            "demo_records": [record.to_doc() for record in self.demo_records],
            "reset_steps": list(self.reset_steps),
            "notes": self.notes,
        }


def mark_demo_only_record(
    record_type: str,
    record_ref: str,
    *,
    resettable: bool = True,
    session_scope: str = "Disposable",
    notes: str = "",
) -> ShowcaseDemoRecord:
    """Return one showcase-only record marker."""

    record_type_value = _clean_text(record_type)
    record_ref_value = _clean_text(record_ref)
    if not record_type_value:
        raise ValueError("record_type is required")
    if not record_ref_value:
        raise ValueError("record_ref is required")
    return ShowcaseDemoRecord(
        record_type=record_type_value,
        record_ref=record_ref_value,
        demo_only=True,
        resettable=resettable,
        session_scope=_clean_text(session_scope) or "Disposable",
        notes=_clean_text(notes),
    )


def controlled_demo_actions() -> tuple[str, ...]:
    """Return the supported showcase action set."""

    return SHOWCASE_CONTROLLED_ACTIONS


def screenshare_demo_checklist() -> tuple[str, ...]:
    """Return the screenshare checklist for showcase runs."""

    return SHOWCASE_SCREENSHARE_CHECKLIST


def public_demo_checklist() -> tuple[str, ...]:
    """Return the public demo checklist for showcase runs."""

    return SHOWCASE_PUBLIC_DEMO_CHECKLIST


def build_showcase_seed_plan(
    *,
    public_host: str,
    backend_host: str,
    catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow] = (),
    order_rows: Iterable[Mapping[str, Any] | StorefrontOrder] = (),
    session_cookie_name: str = SHOWCASE_SESSION_COOKIE_NAME,
    disposable_session_label: str = "Disposable showcase session",
    notes: str = "",
) -> ShowcaseSeedPlan:
    """Return one safe showcase seed plan."""

    public_host_value = _clean_text(public_host)
    backend_host_value = _clean_text(backend_host)
    if not public_host_value:
        raise ValueError("public_host is required")
    if not backend_host_value:
        raise ValueError("backend_host is required")
    normalized_catalog_rows = tuple(
        _normalize_catalog_row(catalog_row) for catalog_row in catalog_rows
    )
    if not normalized_catalog_rows:
        normalized_catalog_rows = StorefrontSimulatorAdapter(
            storefront_host=public_host_value,
        ).sample_catalog_rows()
    normalized_orders = tuple(
        _normalize_order(
            order_row,
            public_host=public_host_value,
            session_cookie_name=session_cookie_name,
        )
        for order_row in order_rows
    )
    if not normalized_orders:
        normalized_orders = (
            _build_demo_order(
                public_host_value,
                session_cookie_name,
                disposable_session_label,
                normalized_catalog_rows,
            ),
        )
    demo_records = tuple(
        mark_demo_only_record(
            "Catalog",
            catalog_row.sku,
            session_scope="Disposable",
            notes=catalog_row.notes,
        )
        for catalog_row in normalized_catalog_rows
    ) + tuple(
        mark_demo_only_record(
            "Order",
            order_row.order_id,
            session_scope=disposable_session_label,
            notes=order_row.notes,
        )
        for order_row in normalized_orders
    )
    return ShowcaseSeedPlan(
        public_host=public_host_value,
        backend_host=backend_host_value,
        session_cookie_name=_clean_text(session_cookie_name)
        or SHOWCASE_SESSION_COOKIE_NAME,
        disposable_session_label=_clean_text(disposable_session_label)
        or "Disposable showcase session",
        catalog_rows=normalized_catalog_rows,
        order_rows=normalized_orders,
        demo_records=demo_records,
        notes=_clean_text(notes),
    )


def build_showcase_reset_plan(
    seed_plan: ShowcaseSeedPlan,
    *,
    production_record_refs: Iterable[str] = (),
    notes: str = "",
) -> ShowcaseResetPlan:
    """Return the reset plan for a safe showcase seed plan."""

    overlap = {
        ref
        for ref in (_clean_text(value) for value in production_record_refs)
        if ref
    }
    conflicting_refs = tuple(
        sorted(set(seed_plan.demo_record_refs()).intersection(overlap))
    )
    if conflicting_refs:
        raise ValueError(
            "showcase demo state overlaps production state: "
            + ", ".join(conflicting_refs)
        )
    reset_notes = _clean_text(notes) or seed_plan.notes
    return ShowcaseResetPlan(
        public_host=seed_plan.public_host,
        backend_host=seed_plan.backend_host,
        session_cookie_name=seed_plan.session_cookie_name,
        disposable_session_label=seed_plan.disposable_session_label,
        demo_records=seed_plan.demo_records,
        notes=reset_notes,
    )


__all__ = [
    "SHOWCASE_CONTROLLED_ACTIONS",
    "SHOWCASE_PUBLIC_DEMO_CHECKLIST",
    "SHOWCASE_RESET_STEPS",
    "SHOWCASE_SCREENSHARE_CHECKLIST",
    "SHOWCASE_SESSION_COOKIE_NAME",
    "ShowcaseDemoRecord",
    "ShowcaseResetPlan",
    "ShowcaseSeedPlan",
    "build_showcase_reset_plan",
    "build_showcase_seed_plan",
    "controlled_demo_actions",
    "mark_demo_only_record",
    "public_demo_checklist",
    "screenshare_demo_checklist",
]
