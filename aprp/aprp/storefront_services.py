"""APRP storefront sync service helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Protocol, runtime_checkable

from .storefront_contract import (
    StorefrontCatalogRow,
    StorefrontOrder,
    StorefrontOrderLine,
)

EVENT_TYPES = ("Catalog", "Order", "Reservation", "Refund", "Customer")
SYNC_STATUSES = ("Pending", "Synced", "Failed")
BATCH_STATUSES = ("Draft", "In Progress", "Synced", "Failed")


def _clean_text(value: Any) -> str:
    """Return a stripped string representation for sync fields."""

    if value is None:
        return ""
    return str(value).strip()


def _coerce_bool(value: Any) -> bool:
    """Return a stable boolean representation for sync inputs."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _coerce_float(value: Any) -> float:
    """Return a float representation for sync quantity inputs."""

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
    raise TypeError(f"unsupported storefront sync input: {type(value)!r}")


def _visible_stock_qty(stock_qty: Any, web_buffer_qty: Any) -> float:
    """Return the public stock quantity after applying the web buffer."""

    return round(
        max(_coerce_float(stock_qty) - _coerce_float(web_buffer_qty), 0.0),
        2,
    )


def _normalize_catalog_row(
    value: Mapping[str, Any] | StorefrontCatalogRow,
) -> StorefrontCatalogRow:
    """Return a normalized storefront catalog row."""

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


def _normalize_event_type(event_type: Any) -> str:
    """Return a canonical sync event type."""

    normalized = _clean_text(event_type).title()
    if normalized not in EVENT_TYPES:
        raise ValueError(f"unsupported sync event type: {event_type!r}")
    return normalized


def _normalize_sync_status(sync_status: Any) -> str:
    """Return a canonical sync status."""

    normalized = _clean_text(sync_status).title()
    if normalized not in SYNC_STATUSES:
        raise ValueError(f"unsupported sync status: {sync_status!r}")
    return normalized


def _derive_batch_status(
    requested_status: str,
    started_on: str,
    finished_on: str,
    events: tuple["StorefrontSyncEventDraft", ...],
    catalog_row_count: int,
    order_row_count: int,
) -> str:
    """Return the most appropriate batch status."""

    if requested_status:
        return requested_status
    event_statuses = tuple(event.sync_status for event in events)
    if "Failed" in event_statuses:
        return "Failed"
    if finished_on:
        return "Synced"
    if started_on or catalog_row_count or order_row_count:
        return "In Progress"
    return "Draft"


@dataclass(frozen=True)
class StorefrontProductSyncPayload:
    """Describe one storefront product sync payload."""

    sku: str
    name: str
    description: str
    price_eur: float
    stock_qty: float
    visible_stock_qty: float
    publication_state: str
    availability_state: str
    backorders_allowed: bool
    tax_class: str
    shipping_class: str
    language: str
    publishable: bool
    notes: str
    web_buffer_qty: float

    def to_doc(self) -> dict[str, Any]:
        """Return the payload as a plain dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class StorefrontStockSyncPayload:
    """Describe one storefront stock sync payload."""

    sku: str
    warehouse: str
    raw_quantity: float
    available_quantity: float
    web_buffer_qty: float
    backorders_allowed: bool
    pack_family: str
    notes: str

    def to_doc(self) -> dict[str, Any]:
        """Return the payload as a plain dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class StorefrontAvailabilitySyncPayload:
    """Describe one storefront availability sync payload."""

    sku: str
    publication_state: str
    availability_state: str
    available_quantity: float
    backorders_allowed: bool
    publishable: bool
    notes: str

    def to_doc(self) -> dict[str, Any]:
        """Return the payload as a plain dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class StorefrontSyncEventDraft:
    """Describe one storefront sync event draft."""

    event_type: str
    source_ref: str
    product_profile: str = ""
    sync_status: str = "Pending"
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this sync event."""

        return {
            "event_type": self.event_type,
            "source_ref": self.source_ref,
            "product_profile": self.product_profile,
            "sync_status": self.sync_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class StorefrontSyncBatchDraft:
    """Describe one storefront sync batch draft."""

    batch_id: str
    storefront_host: str
    status: str = "Draft"
    started_on: str = ""
    finished_on: str = ""
    catalog_rows: int = 0
    order_rows: int = 0
    notes: str = ""
    events: tuple[StorefrontSyncEventDraft, ...] = ()

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this sync batch."""

        return {
            "batch_id": self.batch_id,
            "storefront_host": self.storefront_host,
            "status": self.status,
            "started_on": self.started_on,
            "finished_on": self.finished_on,
            "catalog_rows": self.catalog_rows,
            "order_rows": self.order_rows,
            "notes": self.notes,
            "events": [event.to_doc() for event in self.events],
        }


@runtime_checkable
class StorefrontAdapter(Protocol):
    """Describe the storefront adapter contract."""

    adapter_name: str
    storefront_host: str
    https_only: bool

    def build_product_sync_payloads(
        self,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
    ) -> tuple[StorefrontProductSyncPayload, ...]:
        """Return publishable product payloads for the storefront."""

    def build_stock_sync_payloads(
        self,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
    ) -> tuple[StorefrontStockSyncPayload, ...]:
        """Return stock payloads for the storefront."""

    def build_availability_sync_payloads(
        self,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
    ) -> tuple[StorefrontAvailabilitySyncPayload, ...]:
        """Return availability payloads for the storefront."""

    def build_sync_event(
        self,
        *,
        event_type: str,
        source_ref: str,
        product_profile: str = "",
        sync_status: str = "Pending",
        notes: str = "",
    ) -> StorefrontSyncEventDraft:
        """Return one storefront sync event draft."""

    def build_sync_batch(
        self,
        *,
        batch_id: str,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
        order_rows: Iterable[Mapping[str, Any] | StorefrontOrder] = (),
        status: str = "",
        started_on: str = "",
        finished_on: str = "",
        notes: str = "",
    ) -> StorefrontSyncBatchDraft:
        """Return one storefront sync batch draft."""

    def ingest_order(
        self,
        order: Mapping[str, Any] | StorefrontOrder,
        *,
        storefront_host: str = "",
        customer_ref: str = "",
        order_lines: Iterable[Mapping[str, Any] | StorefrontOrderLine] = (),
        order_id: str = "",
        currency: str = "EUR",
        order_state: str = "Pending",
        payment_state: str = "Pending",
        https_only: bool = True,
        public_session_id: str = "",
        source_language: str = "bg",
        notes: str = "",
    ) -> StorefrontOrder:
        """Return one normalized storefront order."""


@dataclass(frozen=True)
class _StorefrontAdapterBase:
    """Shared adapter behavior for storefront sync proof helpers."""

    storefront_host: str
    https_only: bool = True
    adapter_name: str = "APRP Storefront"

    def build_product_sync_payloads(
        self,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
    ) -> tuple[StorefrontProductSyncPayload, ...]:
        """Return publishable product payloads for the storefront."""

        payloads = []
        for catalog_row in catalog_rows:
            normalized_row = _normalize_catalog_row(catalog_row)
            if normalized_row.is_publishable():
                payloads.append(_build_product_sync_payload(normalized_row))
        return tuple(payloads)

    def build_stock_sync_payloads(
        self,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
    ) -> tuple[StorefrontStockSyncPayload, ...]:
        """Return stock payloads for the storefront."""

        return tuple(
            _build_stock_sync_payload(_normalize_catalog_row(catalog_row))
            for catalog_row in catalog_rows
        )

    def build_availability_sync_payloads(
        self,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
    ) -> tuple[StorefrontAvailabilitySyncPayload, ...]:
        """Return availability payloads for the storefront."""

        return tuple(
            _build_availability_sync_payload(
                _normalize_catalog_row(catalog_row)
            )
            for catalog_row in catalog_rows
        )

    def build_sync_event(
        self,
        *,
        event_type: str,
        source_ref: str,
        product_profile: str = "",
        sync_status: str = "Pending",
        notes: str = "",
    ) -> StorefrontSyncEventDraft:
        """Return one storefront sync event draft."""

        return StorefrontSyncEventDraft(
            event_type=_normalize_event_type(event_type),
            source_ref=_clean_text(source_ref),
            product_profile=_clean_text(product_profile),
            sync_status=_normalize_sync_status(sync_status),
            notes=_clean_text(notes),
        )

    def build_sync_batch(
        self,
        *,
        batch_id: str,
        catalog_rows: Iterable[Mapping[str, Any] | StorefrontCatalogRow],
        order_rows: Iterable[Mapping[str, Any] | StorefrontOrder] = (),
        status: str = "",
        started_on: str = "",
        finished_on: str = "",
        notes: str = "",
    ) -> StorefrontSyncBatchDraft:
        """Return one storefront sync batch draft."""

        normalized_catalog_rows = tuple(
            _normalize_catalog_row(catalog_row) for catalog_row in catalog_rows
        )
        product_payloads = self.build_product_sync_payloads(
            normalized_catalog_rows
        )
        self.build_stock_sync_payloads(normalized_catalog_rows)
        self.build_availability_sync_payloads(normalized_catalog_rows)
        normalized_orders = tuple(
            self.ingest_order(order_row) for order_row in order_rows
        )
        events = [
            self.build_sync_event(
                event_type="Catalog",
                source_ref=payload.sku,
                product_profile=payload.name,
                sync_status="Synced",
            )
            for payload in product_payloads
        ]
        skipped_rows = [
            catalog_row
            for catalog_row in normalized_catalog_rows
            if not catalog_row.is_publishable()
        ]
        events.extend(
            self.build_sync_event(
                event_type="Catalog",
                source_ref=catalog_row.sku,
                product_profile=catalog_row.item_name,
                sync_status="Failed",
                notes="Blocked from publication",
            )
            for catalog_row in skipped_rows
        )
        events.extend(
            self.build_sync_event(
                event_type="Order",
                source_ref=order.order_id,
                sync_status="Failed" if order.needs_review() else "Synced",
                notes="Order requires review" if order.needs_review() else "",
            )
            for order in normalized_orders
        )
        selected_status = _derive_batch_status(
            _clean_text(status),
            _clean_text(started_on),
            _clean_text(finished_on),
            tuple(events),
            len(product_payloads),
            len(normalized_orders),
        )
        if selected_status not in BATCH_STATUSES:
            raise ValueError(f"unsupported batch status: {selected_status!r}")
        if not batch_id:
            raise ValueError("batch_id is required")
        if not self.storefront_host:
            raise ValueError("storefront_host is required")
        return StorefrontSyncBatchDraft(
            batch_id=_clean_text(batch_id),
            storefront_host=self.storefront_host,
            status=selected_status,
            started_on=_clean_text(started_on),
            finished_on=_clean_text(finished_on),
            catalog_rows=len(normalized_catalog_rows),
            order_rows=len(normalized_orders),
            notes=_clean_text(notes),
            events=tuple(events),
        )

    def ingest_order(
        self,
        order: Mapping[str, Any] | StorefrontOrder,
        *,
        storefront_host: str = "",
        customer_ref: str = "",
        order_lines: Iterable[Mapping[str, Any] | StorefrontOrderLine] = (),
        order_id: str = "",
        currency: str = "EUR",
        order_state: str = "Pending",
        payment_state: str = "Pending",
        https_only: bool = True,
        public_session_id: str = "",
        source_language: str = "bg",
        notes: str = "",
    ) -> StorefrontOrder:
        """Return one normalized storefront order."""

        return _ingest_storefront_order(
            order,
            storefront_host=storefront_host or self.storefront_host,
            customer_ref=customer_ref,
            order_lines=order_lines,
            order_id=order_id,
            currency=currency,
            order_state=order_state,
            payment_state=payment_state,
            https_only=https_only,
            public_session_id=public_session_id,
            source_language=source_language,
            notes=notes,
        )


@dataclass(frozen=True)
class StorefrontSimulatorAdapter(_StorefrontAdapterBase):
    """Describe the local storefront simulator adapter shell."""

    adapter_name: str = "Simulator"

    def sample_catalog_rows(self) -> tuple[StorefrontCatalogRow, ...]:
        """Return sample catalog rows for proof and smoke tests."""

        return (
            StorefrontCatalogRow(
                item_code="APRP-ITEM-001",
                sku="SKU-001",
                item_name="APRP Starter Box",
                price_eur=19.9,
                stock_qty=12,
                web_buffer_qty=2,
                publication_state="Publish",
                availability_state="Available",
                backorders_allowed=False,
                tax_class="Standard",
                shipping_class="Box",
                language="bg",
                notes="Sample publishable storefront row.",
            ),
            StorefrontCatalogRow(
                item_code="APRP-ITEM-002",
                sku="SKU-002",
                item_name="APRP Hidden Box",
                price_eur=25.0,
                stock_qty=6,
                web_buffer_qty=0,
                publication_state="Hidden",
                availability_state="Available",
                backorders_allowed=False,
                tax_class="Standard",
                shipping_class="Box",
                language="bg",
                notes="Sample blocked storefront row.",
            ),
        )


@dataclass(frozen=True)
class StorefrontWooCommerceAdapter(_StorefrontAdapterBase):
    """Describe the WooCommerce adapter shell."""

    api_base_url: str = ""
    consumer_key: str = ""
    consumer_secret: str = ""
    adapter_name: str = "WooCommerce"


def _build_product_sync_payload(
    catalog_row: StorefrontCatalogRow,
) -> StorefrontProductSyncPayload:
    """Return one product sync payload for a catalog row."""

    return StorefrontProductSyncPayload(
        sku=catalog_row.sku,
        name=catalog_row.item_name,
        description=catalog_row.notes,
        price_eur=catalog_row.price_eur,
        stock_qty=catalog_row.stock_qty,
        visible_stock_qty=catalog_row.visible_stock_qty(),
        publication_state=catalog_row.publication_state,
        availability_state=catalog_row.availability_state,
        backorders_allowed=catalog_row.backorders_allowed,
        tax_class=catalog_row.tax_class,
        shipping_class=catalog_row.shipping_class,
        language=catalog_row.language,
        publishable=catalog_row.is_publishable(),
        notes=catalog_row.notes,
        web_buffer_qty=catalog_row.web_buffer_qty,
    )


def _build_stock_sync_payload(
    catalog_row: StorefrontCatalogRow,
) -> StorefrontStockSyncPayload:
    """Return one stock sync payload for a catalog row."""

    return StorefrontStockSyncPayload(
        sku=catalog_row.sku,
        warehouse=catalog_row.item_code,
        raw_quantity=catalog_row.stock_qty,
        available_quantity=catalog_row.visible_stock_qty(),
        web_buffer_qty=catalog_row.web_buffer_qty,
        backorders_allowed=catalog_row.backorders_allowed,
        pack_family="",
        notes=catalog_row.notes,
    )


def _build_availability_sync_payload(
    catalog_row: StorefrontCatalogRow,
) -> StorefrontAvailabilitySyncPayload:
    """Return one availability sync payload for a catalog row."""

    return StorefrontAvailabilitySyncPayload(
        sku=catalog_row.sku,
        publication_state=catalog_row.publication_state,
        availability_state=catalog_row.availability_state,
        available_quantity=catalog_row.visible_stock_qty(),
        backorders_allowed=catalog_row.backorders_allowed,
        publishable=catalog_row.is_publishable(),
        notes=catalog_row.notes,
    )


def _ingest_storefront_order(
    order: Mapping[str, Any] | StorefrontOrder,
    *,
    storefront_host: str = "",
    customer_ref: str = "",
    order_lines: Iterable[Mapping[str, Any] | StorefrontOrderLine] = (),
    order_id: str = "",
    currency: str = "EUR",
    order_state: str = "Pending",
    payment_state: str = "Pending",
    https_only: bool = True,
    public_session_id: str = "",
    source_language: str = "bg",
    notes: str = "",
) -> StorefrontOrder:
    """Return one normalized storefront order."""

    order_data = _mapping_from_input(order)
    order_lines_input = order_data.get("order_lines", order_lines)
    normalized_lines = tuple(
        _normalize_order_line(order_line) for order_line in order_lines_input
    )
    order_identifier = _clean_text(order_data.get("order_id")) or _clean_text(
        order_id
    )
    storefront_host_value = _clean_text(
        order_data.get("storefront_host")
    ) or _clean_text(storefront_host)
    customer_reference = _clean_text(
        order_data.get("customer_ref")
    ) or _clean_text(customer_ref)
    if not order_identifier:
        raise ValueError("order_id is required")
    if not storefront_host_value:
        raise ValueError("storefront_host is required")
    if not customer_reference:
        raise ValueError("customer_ref is required")
    if not normalized_lines:
        raise ValueError("order_lines are required")
    return StorefrontOrder(
        order_id=order_identifier,
        storefront_host=storefront_host_value,
        customer_ref=customer_reference,
        currency=_clean_text(order_data.get("currency")) or currency,
        order_state=_clean_text(order_data.get("order_state")) or order_state,
        payment_state=_clean_text(order_data.get("payment_state"))
        or payment_state,
        https_only=(
            _coerce_bool(order_data.get("https_only"))
            if "https_only" in order_data
            else https_only
        ),
        public_session_id=_clean_text(order_data.get("public_session_id"))
        or public_session_id,
        source_language=_clean_text(order_data.get("source_language"))
        or source_language,
        order_lines=normalized_lines,
        notes=_clean_text(order_data.get("notes")) or notes,
    )


__all__ = [
    "StorefrontAdapter",
    "StorefrontAvailabilitySyncPayload",
    "StorefrontProductSyncPayload",
    "StorefrontSimulatorAdapter",
    "StorefrontStockSyncPayload",
    "StorefrontSyncBatchDraft",
    "StorefrontSyncEventDraft",
    "StorefrontWooCommerceAdapter",
]
