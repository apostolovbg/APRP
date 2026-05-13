"""Core APRP storefront synchronization contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StorefrontCatalogRow:
    """Describe one ERP-controlled storefront listing row."""

    item_code: str
    sku: str
    item_name: str
    price_eur: float
    stock_qty: float = 0.0
    web_buffer_qty: float = 0.0
    publication_state: str = "Hidden"
    availability_state: str = "Unknown"
    backorders_allowed: bool = False
    tax_class: str = ""
    shipping_class: str = ""
    language: str = "bg"
    notes: str = ""

    def storefront_key(self) -> str:
        """Return the stable storefront key for one listing row."""

        return self.sku.strip()

    def visible_stock_qty(self) -> float:
        """Return the stock quantity that the storefront may expose."""

        return round(max(self.stock_qty - self.web_buffer_qty, 0.0), 2)

    def is_publishable(self) -> bool:
        """Return whether the row may be published to the storefront."""

        state = self.publication_state.strip().lower()
        availability = self.availability_state.strip().lower()
        return (
            state == "publish"
            and availability not in {"blocked", "unsafe"}
            and (self.visible_stock_qty() > 0 or self.backorders_allowed)
        )

    def needs_review(self) -> bool:
        """Return whether the row needs operator review before publishing."""

        state = self.publication_state.strip().lower()
        availability = self.availability_state.strip().lower()
        return state != "publish" or availability in {"blocked", "unsafe"}


@dataclass(frozen=True)
class StorefrontOrderLine:
    """Describe one storefront order line awaiting ERP reservation."""

    item_code: str
    sku: str
    item_name: str
    quantity: float
    unit_price_eur: float
    tax_rate: float = 0.0
    warehouse: str = ""
    reservation_state: str = "Pending"
    notes: str = ""

    def line_total_eur(self) -> float:
        """Return the pre-tax line total."""

        return round(self.quantity * self.unit_price_eur, 2)

    def requires_reservation(self) -> bool:
        """Return whether the line still needs ERP reservation work."""

        return self.reservation_state.strip().lower() != "reserved"


@dataclass(frozen=True)
class StorefrontOrder:
    """Describe one storefront order imported into ERP."""

    order_id: str
    storefront_host: str
    customer_ref: str
    currency: str = "EUR"
    order_state: str = "Pending"
    payment_state: str = "Pending"
    https_only: bool = True
    public_session_id: str = ""
    source_language: str = "bg"
    order_lines: tuple[StorefrontOrderLine, ...] = ()
    notes: str = ""

    def line_count(self) -> int:
        """Return the number of order lines in the storefront order."""

        return len(self.order_lines)

    def gross_total_eur(self) -> float:
        """Return the total order amount before ERP adjustments."""

        return round(
            sum(line.line_total_eur() for line in self.order_lines),
            2,
        )

    def requires_erp_reservation(self) -> bool:
        """Return whether the order still needs ERP reservation work."""

        return any(line.requires_reservation() for line in self.order_lines)

    def needs_review(self) -> bool:
        """Return whether the order should be flagged for operator review."""

        order_state = self.order_state.strip().lower()
        payment_state = self.payment_state.strip().lower()
        if not self.https_only:
            return True
        if order_state in {"cancelled", "failed"}:
            return True
        if payment_state in {"unknown", "failed"}:
            return True
        return any(line.quantity <= 0 for line in self.order_lines)


@dataclass(frozen=True)
class StorefrontReservation:
    """Describe one ERP reservation created from a storefront order."""

    reservation_id: str
    order_id: str
    item_code: str
    sku: str
    warehouse: str
    quantity: float
    reservation_state: str = "Reserved"
    fulfillment_state: str = "Pending"
    payment_state: str = "Pending"
    notes: str = ""

    def is_active(self) -> bool:
        """Return whether the reservation is still active in ERP."""

        return self.reservation_state.strip().lower() in {"held", "reserved"}

    def needs_review(self) -> bool:
        """Return whether the reservation requires operator review."""

        if self.quantity <= 0:
            return True
        return self.reservation_state.strip().lower() not in {
            "held",
            "reserved",
            "released",
        }


@dataclass(frozen=True)
class StorefrontSyncBatch:
    """Describe one storefront sync pass and its ERP inputs."""

    batch_id: str
    storefront_host: str
    https_only: bool = True
    catalog_rows: tuple[StorefrontCatalogRow, ...] = ()
    orders: tuple[StorefrontOrder, ...] = ()
    reservations: tuple[StorefrontReservation, ...] = ()
    notes: str = ""

    def publishable_rows(self) -> tuple[StorefrontCatalogRow, ...]:
        """Return the catalog rows that can safely be published."""

        return tuple(row for row in self.catalog_rows if row.is_publishable())

    def visible_stock_qty(self) -> float:
        """Return the total stock that may be exposed publicly."""

        return round(
            sum(row.visible_stock_qty() for row in self.publishable_rows()),
            2,
        )

    def gross_order_total_eur(self) -> float:
        """Return the gross total imported from storefront orders."""

        return round(sum(order.gross_total_eur() for order in self.orders), 2)

    def review_required(self) -> bool:
        """Return whether the sync batch requires operator review."""

        return (
            not self.https_only
            or any(row.needs_review() for row in self.catalog_rows)
            or any(order.needs_review() for order in self.orders)
            or any(
                reservation.needs_review() for reservation in self.reservations
            )
        )


@dataclass(frozen=True)
class StorefrontSyncSummary:
    """Describe one operator-facing storefront sync summary."""

    batch_id: str
    storefront_host: str
    catalog_count: int
    publishable_count: int
    order_count: int
    reservation_count: int
    visible_stock_qty: float
    gross_order_total_eur: float
    https_only: bool
    review_required: bool

    def is_ready_to_sync(self) -> bool:
        """Return whether the storefront batch is safe to sync."""

        return self.https_only and not self.review_required


def build_storefront_sync_summary(
    batch: StorefrontSyncBatch,
) -> StorefrontSyncSummary:
    """Build a storefront sync summary from one batch of ERP truth."""

    return StorefrontSyncSummary(
        batch_id=batch.batch_id,
        storefront_host=batch.storefront_host,
        catalog_count=len(batch.catalog_rows),
        publishable_count=len(batch.publishable_rows()),
        order_count=len(batch.orders),
        reservation_count=len(batch.reservations),
        visible_stock_qty=batch.visible_stock_qty(),
        gross_order_total_eur=batch.gross_order_total_eur(),
        https_only=batch.https_only,
        review_required=batch.review_required(),
    )


__all__ = [
    "StorefrontCatalogRow",
    "StorefrontOrder",
    "StorefrontOrderLine",
    "StorefrontReservation",
    "StorefrontSyncBatch",
    "StorefrontSyncSummary",
    "build_storefront_sync_summary",
]
