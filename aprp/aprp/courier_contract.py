"""Core APRP courier, COD, and return contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

COURIER_TARGETS: Final[tuple[str, ...]] = ("Speedy", "Econt")
COURIER_SERVICE_MODES: Final[tuple[str, ...]] = (
    "Office Pickup",
    "Address Delivery",
    "Store Pickup",
)
COURIER_EVENT_TYPES: Final[tuple[str, ...]] = (
    "label_created",
    "handed_off",
    "delivered",
    "cod_collected",
    "payout_received",
    "returned",
    "exception",
)


def _normalized(text: str) -> str:
    """Return a comparison-safe lower-case representation."""

    return text.strip().lower()


@dataclass(frozen=True)
class CourierCapability:
    """Describe one courier adapter capability profile."""

    courier_name: str
    supports_domestic: bool = True
    supports_international: bool = False
    supports_office_pickup: bool = True
    supports_address_delivery: bool = True
    supports_store_pickup: bool = True
    supports_cod: bool = True
    supports_label_creation: bool = True
    supports_tracking: bool = True
    supports_pickup_requests: bool = True
    supports_returns: bool = True
    notes: str = ""

    def supports_destination(self, destination_country: str) -> bool:
        """Return whether the adapter can serve the destination."""

        country = destination_country.strip().upper()
        if not country:
            return False
        if country == "BG":
            return self.supports_domestic
        return self.supports_international

    def supports_service_mode(self, service_mode: str) -> bool:
        """Return whether the adapter can serve the shipping mode."""

        normalized = _normalized(service_mode)
        if normalized == "office pickup":
            return self.supports_office_pickup
        if normalized == "address delivery":
            return self.supports_address_delivery
        if normalized == "store pickup":
            return self.supports_store_pickup
        return False

    def can_offer_cod(
        self, destination_country: str, service_mode: str
    ) -> bool:
        """Return whether the adapter can offer COD for the shipment."""

        return (
            self.supports_cod
            and destination_country.strip().upper() == "BG"
            and self.supports_destination(destination_country)
            and self.supports_service_mode(service_mode)
        )

    def can_create_shipment(
        self,
        destination_country: str,
        service_mode: str,
    ) -> bool:
        """Return whether the adapter can create a shipment."""

        return (
            self.supports_label_creation
            and self.supports_destination(destination_country)
            and self.supports_service_mode(service_mode)
        )


@dataclass(frozen=True)
class CourierEvent:
    """Describe one courier event that changes ERP truth."""

    event_id: str
    shipment_id: str
    courier_name: str
    event_type: str
    occurred_at: str
    event_state: str = "Recorded"
    tracking_number: str = ""
    label_reference: str = ""
    notes: str = ""

    def event_key(self) -> str:
        """Return the stable key for one courier event."""

        return "|".join(
            [
                self.courier_name.strip(),
                self.shipment_id.strip(),
                self.event_id.strip(),
            ]
        )

    def is_exception(self) -> bool:
        """Return whether the event indicates a delivery exception."""

        event_type = _normalized(self.event_type)
        event_state = _normalized(self.event_state)
        return event_type in {
            "exception",
            "label_failed",
            "delivery_failed",
            "cod_mismatch",
            "payout_mismatch",
        } or event_state in {"failed", "blocked", "requires_review"}

    def affects_return(self) -> bool:
        """Return whether the event changes return state."""

        return _normalized(self.event_type) in {"returned", "return_received"}

    def affects_payment(self) -> bool:
        """Return whether the event changes COD or payout state."""

        return _normalized(self.event_type) in {
            "cod_collected",
            "payout_received",
        }


@dataclass(frozen=True)
class CourierShipment:
    """Describe one shipment and its courier reconciliation state."""

    shipment_id: str
    order_id: str
    courier_name: str
    service_mode: str
    destination_country: str
    shipment_state: str = "Draft"
    label_reference: str = ""
    tracking_number: str = ""
    cod_state: str = "Pending"
    payout_state: str = "Pending"
    return_state: str = "None"
    exception_state: str = "None"
    notes: str = ""

    def shipment_key(self) -> str:
        """Return the stable key for one shipment."""

        return "|".join(
            [
                self.courier_name.strip(),
                self.order_id.strip(),
                self.shipment_id.strip(),
            ]
        )

    def is_domestic(self) -> bool:
        """Return whether the shipment stays within Bulgaria."""

        return self.destination_country.strip().upper() == "BG"

    def has_label(self) -> bool:
        """Return whether the shipment already has a label reference."""

        return bool(self.label_reference.strip())

    def has_tracking(self) -> bool:
        """Return whether the shipment already has a tracking number."""

        return bool(self.tracking_number.strip())

    def has_return(self) -> bool:
        """Return whether the shipment already entered return flow."""

        return _normalized(self.return_state) not in {"", "none"}

    def is_cod_pending(self) -> bool:
        """Return whether COD is still pending confirmation."""

        return _normalized(self.cod_state) == "pending"

    def needs_review(self) -> bool:
        """Return whether the shipment needs operator review."""

        shipment_state = _normalized(self.shipment_state)
        cod_state = _normalized(self.cod_state)
        payout_state = _normalized(self.payout_state)
        return_state = _normalized(self.return_state)
        exception_state = _normalized(self.exception_state)

        if shipment_state in {"failed", "rejected", "blocked"}:
            return True
        if exception_state in {"failed", "blocked", "requires_review"}:
            return True
        if cod_state in {"failed", "mismatch"}:
            return True
        if payout_state in {"failed", "mismatch"}:
            return True
        if return_state in {"failed", "mismatch"}:
            return True
        if (
            shipment_state in {"delivered", "returned"}
            and not self.has_tracking()
        ):
            return True
        return False

    def is_closed(self) -> bool:
        """Return whether the shipment reached a terminal state."""

        return _normalized(self.shipment_state) in {"delivered", "returned"}


@dataclass(frozen=True)
class CourierDispatchBatch:
    """Describe one courier run grouped for review."""

    batch_id: str
    courier_name: str
    shipments: tuple[CourierShipment, ...] = ()
    events: tuple[CourierEvent, ...] = ()
    notes: str = ""

    def shipment_count(self) -> int:
        """Return the number of shipments in the batch."""

        return len(self.shipments)

    def event_count(self) -> int:
        """Return the number of courier events in the batch."""

        return len(self.events)

    def tracking_count(self) -> int:
        """Return the number of shipments with tracking numbers."""

        return sum(1 for shipment in self.shipments if shipment.has_tracking())

    def cod_pending_count(self) -> int:
        """Return the number of shipments still waiting on COD."""

        return sum(
            1 for shipment in self.shipments if shipment.is_cod_pending()
        )

    def return_count(self) -> int:
        """Return the number of shipments already in return flow."""

        return sum(1 for shipment in self.shipments if shipment.has_return())

    def exception_count(self) -> int:
        """Return the number of events that require review."""

        return sum(1 for event in self.events if event.is_exception())

    def review_required(self) -> bool:
        """Return whether the batch still needs operator review."""

        return any(shipment.needs_review() for shipment in self.shipments) or (
            self.exception_count() > 0
        )


@dataclass(frozen=True)
class CourierSummary:
    """Describe one operator-facing courier reconciliation summary."""

    batch_id: str
    courier_name: str
    shipment_count: int
    event_count: int
    tracking_count: int
    cod_pending_count: int
    return_count: int
    exception_count: int
    review_required: bool
    notes: str = ""

    def is_ready_to_close(self) -> bool:
        """Return whether the courier batch can close without review."""

        return not self.review_required


def build_courier_summary(batch: CourierDispatchBatch) -> CourierSummary:
    """Build a summary from one courier dispatch batch."""

    return CourierSummary(
        batch_id=batch.batch_id,
        courier_name=batch.courier_name,
        shipment_count=batch.shipment_count(),
        event_count=batch.event_count(),
        tracking_count=batch.tracking_count(),
        cod_pending_count=batch.cod_pending_count(),
        return_count=batch.return_count(),
        exception_count=batch.exception_count(),
        review_required=batch.review_required(),
        notes=batch.notes,
    )


__all__ = [
    "COURIER_EVENT_TYPES",
    "COURIER_SERVICE_MODES",
    "COURIER_TARGETS",
    "CourierCapability",
    "CourierDispatchBatch",
    "CourierEvent",
    "CourierShipment",
    "CourierSummary",
    "build_courier_summary",
]
