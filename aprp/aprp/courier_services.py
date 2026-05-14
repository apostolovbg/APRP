"""APRP courier service helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Protocol, runtime_checkable

from .courier_contract import (
    COURIER_EVENT_TYPES as CONTRACT_COURIER_EVENT_TYPES,
)
from .courier_contract import (
    COURIER_SERVICE_MODES,
    COURIER_TARGETS,
    CourierCapability,
    CourierDispatchBatch,
    CourierEvent,
    CourierShipment,
    CourierSummary,
    build_courier_summary,
)

COURIER_EVENT_TYPES = CONTRACT_COURIER_EVENT_TYPES
DEFAULT_COURIER_TARGETS = COURIER_TARGETS


def _clean_text(value: Any) -> str:
    """Return a stripped text representation for courier fields."""

    if value is None:
        return ""
    return str(value).strip()


def _coerce_bool(value: Any) -> bool:
    """Return a stable boolean representation for courier inputs."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _coerce_float(value: Any) -> float:
    """Return a float representation for courier quantity inputs."""

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
    raise TypeError(f"unsupported courier input: {type(value)!r}")


def _normalize_courier_name(value: Any) -> str:
    """Return a canonical courier name."""

    courier_name = _clean_text(value)
    if not courier_name:
        return ""
    if courier_name.casefold() == "speedy":
        return "Speedy"
    if courier_name.casefold() == "econt":
        return "Econt"
    if courier_name.casefold() == "simulator":
        return "Simulator"
    return courier_name


def _normalize_service_mode(value: Any) -> str:
    """Return a canonical courier service mode."""

    normalized = _clean_text(value).title()
    if normalized not in COURIER_SERVICE_MODES:
        raise ValueError(f"unsupported courier service mode: {value!r}")
    return normalized


def _normalize_destination_country(value: Any) -> str:
    """Return a canonical destination-country code."""

    return _clean_text(value).upper()


def _normalize_event_type(value: Any) -> str:
    """Return a canonical courier event type."""

    normalized = _clean_text(value).lower().replace(" ", "_")
    if normalized not in COURIER_EVENT_TYPES:
        raise ValueError(f"unsupported courier event type: {value!r}")
    return normalized


def _normalize_tracking_reference(
    value: Mapping[str, Any] | "CourierTrackingReferenceDraft" | None,
) -> "CourierTrackingReferenceDraft" | None:
    """Return a normalized tracking reference draft."""

    if value is None:
        return None
    reference_data = _mapping_from_input(value)
    tracking_number = _clean_text(reference_data.get("tracking_number"))
    label_reference = _clean_text(reference_data.get("label_reference"))
    captured_at = _clean_text(reference_data.get("captured_at"))
    courier_name = _normalize_courier_name(reference_data.get("courier_name"))
    shipment_id = _clean_text(reference_data.get("shipment_id"))
    notes = _clean_text(reference_data.get("notes"))
    if not tracking_number and not label_reference:
        return None
    return CourierTrackingReferenceDraft(
        courier_name=courier_name,
        shipment_id=shipment_id,
        tracking_number=tracking_number,
        label_reference=label_reference,
        captured_at=captured_at,
        notes=notes,
    )


def _normalize_courier_shipment(
    value: Mapping[str, Any] | CourierShipment | "CourierShipmentDraft",
    *,
    courier_name: str = "",
) -> CourierShipment:
    """Return a normalized courier shipment contract."""

    shipment_data = _mapping_from_input(value)
    tracking_reference = _normalize_tracking_reference(
        shipment_data.get("tracking_reference")
    )
    shipment_courier = _normalize_courier_name(
        shipment_data.get("courier_name")
        or shipment_data.get("courier")
        or shipment_data.get("carrier")
        or courier_name
    )
    service_mode = _clean_text(shipment_data.get("service_mode"))
    if service_mode:
        service_mode = _normalize_service_mode(service_mode)
    destination_country = _normalize_destination_country(
        shipment_data.get("destination_country")
    )
    shipment_state = _clean_text(shipment_data.get("shipment_state"))
    if not shipment_state:
        shipment_state = "Draft"
    cod_state = _clean_text(shipment_data.get("cod_state")) or "Pending"
    payout_state = _clean_text(shipment_data.get("payout_state")) or "Pending"
    return_state = _clean_text(shipment_data.get("return_state")) or "None"
    exception_state = (
        _clean_text(shipment_data.get("exception_state")) or "None"
    )
    label_reference = _clean_text(shipment_data.get("label_reference"))
    tracking_number = _clean_text(shipment_data.get("tracking_number"))
    if tracking_reference is not None:
        if not label_reference:
            label_reference = tracking_reference.label_reference
        if not tracking_number:
            tracking_number = tracking_reference.tracking_number
    order_id = _clean_text(shipment_data.get("order_id"))
    shipment_id = _clean_text(shipment_data.get("shipment_id"))
    notes = _clean_text(shipment_data.get("notes"))
    if not shipment_id:
        raise ValueError("shipment_id is required")
    if not order_id:
        raise ValueError("order_id is required")
    if not shipment_courier:
        raise ValueError("courier_name is required")
    if not service_mode:
        raise ValueError("service_mode is required")
    if not destination_country:
        raise ValueError("destination_country is required")
    return CourierShipment(
        shipment_id=shipment_id,
        order_id=order_id,
        courier_name=shipment_courier,
        service_mode=service_mode,
        destination_country=destination_country,
        shipment_state=shipment_state,
        label_reference=label_reference,
        tracking_number=tracking_number,
        cod_state=cod_state,
        payout_state=payout_state,
        return_state=return_state,
        exception_state=exception_state,
        notes=notes,
    )


def _normalize_courier_event(
    value: Mapping[str, Any] | CourierEvent | "CourierEventDraft",
    *,
    courier_name: str = "",
) -> CourierEvent:
    """Return a normalized courier event contract."""

    event_data = _mapping_from_input(value)
    event_courier = _normalize_courier_name(
        event_data.get("courier_name")
        or event_data.get("courier")
        or event_data.get("carrier")
        or courier_name
    )
    event_type = _normalize_event_type(event_data.get("event_type"))
    shipment_id = _clean_text(event_data.get("shipment_id"))
    event_id = _clean_text(event_data.get("event_id"))
    occurred_at = _clean_text(event_data.get("occurred_at"))
    event_state = _clean_text(event_data.get("event_state")) or "Recorded"
    tracking_number = _clean_text(event_data.get("tracking_number"))
    label_reference = _clean_text(event_data.get("label_reference"))
    if not event_id:
        raise ValueError("event_id is required")
    if not shipment_id:
        raise ValueError("shipment_id is required")
    if not event_courier:
        raise ValueError("courier_name is required")
    if not occurred_at:
        raise ValueError("occurred_at is required")
    return CourierEvent(
        event_id=event_id,
        shipment_id=shipment_id,
        courier_name=event_courier,
        event_type=event_type,
        occurred_at=occurred_at,
        event_state=event_state,
        tracking_number=tracking_number,
        label_reference=label_reference,
        notes=_clean_text(event_data.get("notes")),
    )


def _shipment_validation_blockers(
    shipment: CourierShipment,
    *,
    adapter: "CourierAdapter" | None = None,
) -> tuple[str, ...]:
    """Return the structural blockers for one shipment."""

    blockers: list[str] = []
    if not shipment.shipment_id.strip():
        blockers.append("shipment_id")
    if not shipment.order_id.strip():
        blockers.append("order_id")
    if not shipment.courier_name.strip():
        blockers.append("courier_name")
    if not shipment.service_mode.strip():
        blockers.append("service_mode")
    elif shipment.service_mode not in COURIER_SERVICE_MODES:
        blockers.append("service_mode:unsupported")
    if not shipment.destination_country.strip():
        blockers.append("destination_country")
    if (
        shipment.shipment_state.strip().lower()
        in {
            "ready",
            "dispatched",
            "in_transit",
            "delivered",
            "returned",
        }
        and not shipment.label_reference.strip()
    ):
        blockers.append("label_reference")
    if (
        shipment.shipment_state.strip().lower()
        in {
            "dispatched",
            "in_transit",
            "delivered",
            "returned",
        }
        and not shipment.tracking_number.strip()
    ):
        blockers.append("tracking_number")
    if shipment.cod_state.strip().lower() in {"collected", "settled"}:
        if shipment.destination_country.strip().upper() != "BG":
            blockers.append("cod_state")
    if adapter is not None and not adapter.supports_order(
        shipment.destination_country,
        shipment.service_mode,
        requires_cod=shipment.cod_state.strip().lower()
        in {"collected", "settled"},
    ):
        blockers.append("adapter_capability")
    return tuple(blockers)


def _derive_event_state(
    shipment: CourierShipment,
    blockers: tuple[str, ...],
) -> str:
    """Return the most appropriate event state for one shipment."""

    if blockers:
        return "Failed"
    if shipment.needs_review():
        return "Review"
    return "Recorded"


def _derive_event_type(
    shipment: CourierShipment,
    blockers: tuple[str, ...],
) -> str:
    """Return the best event type for one shipment."""

    if blockers:
        return "exception"
    if shipment.needs_review():
        return "exception"
    if (
        shipment.has_return()
        or shipment.shipment_state.strip().lower() == "returned"
    ):
        return "returned"
    if shipment.has_tracking():
        return "handed_off"
    return "label_created"


def _derive_batch_status(
    shipments: tuple["CourierShipmentDraft", ...],
    events: tuple["CourierEventDraft", ...],
    requested_status: str,
) -> str:
    """Return the most appropriate batch status."""

    if requested_status:
        return requested_status
    if not shipments:
        return "Draft"
    if any(draft.validation_blockers for draft in shipments):
        return "Failed"
    if any(event.event_state == "Failed" for event in events):
        return "Failed"
    if any(draft.review_required for draft in shipments):
        return "In Progress"
    if any(event.event_state == "Review" for event in events):
        return "In Progress"
    if all(
        draft.shipment_state.strip().lower() in {"delivered", "returned"}
        for draft in shipments
    ):
        return "Closed"
    return "Ready"


def _derive_operator_state(
    validation_blockers: tuple[str, ...],
    review_required: bool,
    status: str,
) -> str:
    """Return the operator-facing batch state."""

    if validation_blockers:
        return "Blocked"
    if review_required:
        return "Review Required"
    if status == "Closed":
        return "Cleared"
    if status in {"Ready", "In Progress"}:
        return "Queued"
    return "Queued"


@dataclass(frozen=True)
class CourierTrackingReferenceDraft:
    """Describe one captured courier tracking reference."""

    courier_name: str
    shipment_id: str
    tracking_number: str
    label_reference: str
    captured_at: str
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the tracking reference as a plain dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class CourierShipmentDraft:
    """Describe one courier shipment draft."""

    shipment_id: str
    order_id: str
    courier_name: str
    service_mode: str
    destination_country: str
    shipment_state: str = "Draft"
    label_reference: str = ""
    tracking_number: str = ""
    tracking_reference: CourierTrackingReferenceDraft | None = None
    cod_state: str = "Pending"
    payout_state: str = "Pending"
    return_state: str = "None"
    exception_state: str = "None"
    review_required: bool = False
    validation_blockers: tuple[str, ...] = ()
    notes: str = ""

    def has_tracking(self) -> bool:
        """Return whether the shipment already has a tracking number."""

        return bool(self.tracking_number.strip())

    def has_label(self) -> bool:
        """Return whether the shipment already has a label reference."""

        return bool(self.label_reference.strip())

    def needs_review(self) -> bool:
        """Return whether the shipment needs operator review."""

        return self.review_required or bool(self.validation_blockers)

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped shipment payload."""

        return {
            "shipment_id": self.shipment_id,
            "order_id": self.order_id,
            "courier_name": self.courier_name,
            "service_mode": self.service_mode,
            "destination_country": self.destination_country,
            "shipment_state": self.shipment_state,
            "label_reference": self.label_reference,
            "tracking_number": self.tracking_number,
            "tracking_reference": (
                self.tracking_reference.to_doc()
                if self.tracking_reference is not None
                else None
            ),
            "cod_state": self.cod_state,
            "payout_state": self.payout_state,
            "return_state": self.return_state,
            "exception_state": self.exception_state,
            "review_required": self.review_required,
            "validation_blockers": list(self.validation_blockers),
            "notes": self.notes,
        }

    def to_contract(self) -> CourierShipment:
        """Return the canonical courier shipment contract."""

        return CourierShipment(
            shipment_id=self.shipment_id,
            order_id=self.order_id,
            courier_name=self.courier_name,
            service_mode=self.service_mode,
            destination_country=self.destination_country,
            shipment_state=self.shipment_state,
            label_reference=self.label_reference,
            tracking_number=self.tracking_number,
            cod_state=self.cod_state,
            payout_state=self.payout_state,
            return_state=self.return_state,
            exception_state=self.exception_state,
            notes=self.notes,
        )


@dataclass(frozen=True)
class CourierEventDraft:
    """Describe one courier event draft."""

    event_id: str
    shipment_id: str
    courier_name: str
    event_type: str
    occurred_at: str
    event_state: str = "Recorded"
    tracking_number: str = ""
    label_reference: str = ""
    notes: str = ""
    review_required: bool = False
    validation_blockers: tuple[str, ...] = ()

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped event payload."""

        return {
            "event_id": self.event_id,
            "shipment_id": self.shipment_id,
            "courier_name": self.courier_name,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at,
            "event_state": self.event_state,
            "tracking_number": self.tracking_number,
            "label_reference": self.label_reference,
            "notes": self.notes,
        }

    def to_contract(self) -> CourierEvent:
        """Return the canonical courier event contract."""

        return CourierEvent(
            event_id=self.event_id,
            shipment_id=self.shipment_id,
            courier_name=self.courier_name,
            event_type=self.event_type,
            occurred_at=self.occurred_at,
            event_state=self.event_state,
            tracking_number=self.tracking_number,
            label_reference=self.label_reference,
            notes=self.notes,
        )


@dataclass(frozen=True)
class CourierDispatchBatchDraft:
    """Describe one courier dispatch batch draft."""

    batch_id: str
    courier_name: str
    status: str = "Draft"
    notes: str = ""
    shipments: tuple[CourierShipmentDraft, ...] = ()
    events: tuple[CourierEventDraft, ...] = ()
    review_required: bool = False
    validation_blockers: tuple[str, ...] = ()

    def shipment_count(self) -> int:
        """Return the number of shipment drafts in the batch."""

        return len(self.shipments)

    def event_count(self) -> int:
        """Return the number of event drafts in the batch."""

        return len(self.events)

    def tracking_count(self) -> int:
        """Return the number of shipments with tracking references."""

        return sum(1 for shipment in self.shipments if shipment.has_tracking())

    def cod_pending_count(self) -> int:
        """Return the number of shipments still waiting on COD."""

        return sum(
            1 for shipment in self.shipments if shipment.cod_state == "Pending"
        )

    def return_count(self) -> int:
        """Return the number of shipments in return flow."""

        return sum(
            1
            for shipment in self.shipments
            if shipment.return_state.strip().lower() not in {"", "none"}
        )

    def exception_count(self) -> int:
        """Return the number of shipment or event exceptions."""

        return sum(
            1
            for shipment in self.shipments
            if shipment.exception_state.strip().lower() not in {"", "none"}
        ) + sum(1 for event in self.events if event.event_state == "Failed")

    def is_clear(self) -> bool:
        """Return whether the batch can close without review."""

        return not self.review_required and not self.validation_blockers

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped batch payload."""

        return {
            "batch_id": self.batch_id,
            "courier_name": self.courier_name,
            "status": self.status,
            "notes": self.notes,
            "shipments": [shipment.to_doc() for shipment in self.shipments],
            "events": [event.to_doc() for event in self.events],
            "review_required": self.review_required,
            "validation_blockers": list(self.validation_blockers),
        }

    def to_contract(self) -> CourierDispatchBatch:
        """Return the canonical courier dispatch batch contract."""

        return CourierDispatchBatch(
            batch_id=self.batch_id,
            courier_name=self.courier_name,
            shipments=tuple(
                shipment.to_contract() for shipment in self.shipments
            ),
            events=tuple(event.to_contract() for event in self.events),
            notes=self.notes,
        )


@dataclass(frozen=True)
class CourierSummaryDraft:
    """Describe one operator-facing courier summary draft."""

    batch_id: str
    courier_name: str
    shipment_count: int
    event_count: int
    tracking_count: int
    cod_pending_count: int
    return_count: int
    exception_count: int
    review_required: bool
    operator_state: str
    notes: str = ""

    def is_ready_to_close(self) -> bool:
        """Return whether the batch can close without review."""

        return not self.review_required and self.operator_state == "Cleared"

    def to_doc(self) -> dict[str, Any]:
        """Return the summary as a plain dictionary."""

        return asdict(self)

    def to_contract(self) -> CourierSummary:
        """Return the canonical courier summary contract."""

        return CourierSummary(
            batch_id=self.batch_id,
            courier_name=self.courier_name,
            shipment_count=self.shipment_count,
            event_count=self.event_count,
            tracking_count=self.tracking_count,
            cod_pending_count=self.cod_pending_count,
            return_count=self.return_count,
            exception_count=self.exception_count,
            review_required=self.review_required,
            notes=self.notes,
        )


@runtime_checkable
class CourierAdapter(Protocol):
    """Describe the courier adapter contract."""

    adapter_name: str
    courier_name: str
    capabilities: CourierCapability

    def supports_destination(self, destination_country: str) -> bool:
        """Return whether the adapter can serve the destination."""

    def allows_cod_for_destination(self, destination_country: str) -> bool:
        """Return whether the adapter can collect COD for the destination."""

    def supports_service_mode(self, service_mode: str) -> bool:
        """Return whether the adapter can serve the requested mode."""

    def can_offer_cod(
        self,
        destination_country: str,
        service_mode: str,
    ) -> bool:
        """Return whether the adapter can offer COD for the shipment."""

    def can_create_shipment(
        self,
        destination_country: str,
        service_mode: str,
    ) -> bool:
        """Return whether the adapter can create the shipment."""

    def supports_order(
        self,
        destination_country: str,
        service_mode: str,
        *,
        requires_cod: bool = False,
    ) -> bool:
        """Return whether the adapter can serve the requested shipment."""

    def shipment_validation_blockers(
        self,
        shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
    ) -> tuple[str, ...]:
        """Return the structural shipment blockers."""

    def validate_shipment(
        self,
        shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
    ) -> bool:
        """Return whether the shipment is safe to process."""

    def build_courier_shipment_doc(
        self,
        shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
        *,
        notes: str = "",
    ) -> CourierShipmentDraft:
        """Return one normalized courier shipment draft."""

    def build_courier_event_doc(
        self,
        event: Mapping[str, Any] | CourierEvent | CourierEventDraft,
        *,
        notes: str = "",
    ) -> CourierEventDraft:
        """Return one normalized courier event draft."""

    def build_courier_dispatch_batch_doc(
        self,
        *,
        batch_id: str,
        shipments: Iterable[
            Mapping[str, Any] | CourierShipment | CourierShipmentDraft
        ],
        events: Iterable[
            Mapping[str, Any] | CourierEvent | CourierEventDraft
        ] = (),
        status: str = "",
        notes: str = "",
    ) -> CourierDispatchBatchDraft:
        """Return one normalized courier dispatch batch draft."""

    def build_courier_summary_doc(
        self,
        batch: CourierDispatchBatchDraft,
    ) -> CourierSummaryDraft:
        """Return one normalized courier summary draft."""


class _CourierAdapterBase:
    """Shared adapter behavior for courier proof and shell helpers."""

    def __init__(
        self,
        *,
        courier_name: str,
        capabilities: CourierCapability,
        adapter_name: str = "APRP Courier",
    ) -> None:
        """Store the adapter identity and declared capability matrix."""

        self.adapter_name = adapter_name
        self.courier_name = courier_name
        self.capabilities = capabilities

    def supports_destination(self, destination_country: str) -> bool:
        """Return whether the adapter can serve the destination."""

        return self.capabilities.supports_destination(destination_country)

    def allows_cod_for_destination(self, destination_country: str) -> bool:
        """Return whether the adapter can collect COD for the destination."""

        return self.capabilities.can_offer_cod(
            destination_country,
            "Address Delivery",
        )

    def supports_service_mode(self, service_mode: str) -> bool:
        """Return whether the adapter can serve the requested mode."""

        return self.capabilities.supports_service_mode(service_mode)

    def can_offer_cod(
        self,
        destination_country: str,
        service_mode: str,
    ) -> bool:
        """Return whether the adapter can offer COD for the shipment."""

        return self.capabilities.can_offer_cod(
            destination_country,
            service_mode,
        )

    def can_create_shipment(
        self,
        destination_country: str,
        service_mode: str,
    ) -> bool:
        """Return whether the adapter can create the shipment."""

        return self.capabilities.can_create_shipment(
            destination_country,
            service_mode,
        )

    def supports_order(
        self,
        destination_country: str,
        service_mode: str,
        *,
        requires_cod: bool = False,
    ) -> bool:
        """Return whether the adapter can serve the requested shipment."""

        return (
            self.supports_destination(destination_country)
            and self.supports_service_mode(service_mode)
            and (
                not requires_cod
                or self.can_offer_cod(destination_country, service_mode)
            )
        )

    def shipment_validation_blockers(
        self,
        shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
    ) -> tuple[str, ...]:
        """Return the structural shipment blockers."""

        normalized = _normalize_courier_shipment(
            shipment,
            courier_name=self.courier_name,
        )
        return _shipment_validation_blockers(
            normalized,
            adapter=self,
        )

    def validate_shipment(
        self,
        shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
    ) -> bool:
        """Return whether the shipment is safe to process."""

        return not self.shipment_validation_blockers(shipment)

    def build_courier_shipment_doc(
        self,
        shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
        *,
        notes: str = "",
    ) -> CourierShipmentDraft:
        """Return one normalized courier shipment draft."""

        normalized = _normalize_courier_shipment(
            shipment,
            courier_name=self.courier_name,
        )
        shipment_data = _mapping_from_input(shipment)
        blockers = _shipment_validation_blockers(
            normalized,
            adapter=self,
        )
        tracking_reference = _normalize_tracking_reference(
            {
                "courier_name": normalized.courier_name,
                "shipment_id": normalized.shipment_id,
                "tracking_number": normalized.tracking_number,
                "label_reference": normalized.label_reference,
                "captured_at": _clean_text(
                    shipment_data.get("tracking_captured_at")
                    or shipment_data.get("captured_at")
                    or shipment_data.get("occurred_at")
                ),
                "notes": notes,
            }
        )
        review_required = bool(blockers) or normalized.needs_review()
        if normalized.shipment_state.strip().lower() == "returned":
            review_required = (
                review_required or normalized.return_state != "Returned"
            )
        return CourierShipmentDraft(
            shipment_id=normalized.shipment_id,
            order_id=normalized.order_id,
            courier_name=normalized.courier_name,
            service_mode=normalized.service_mode,
            destination_country=normalized.destination_country,
            shipment_state=normalized.shipment_state,
            label_reference=normalized.label_reference,
            tracking_number=normalized.tracking_number,
            tracking_reference=tracking_reference,
            cod_state=normalized.cod_state,
            payout_state=normalized.payout_state,
            return_state=normalized.return_state,
            exception_state=normalized.exception_state,
            review_required=review_required,
            validation_blockers=blockers,
            notes=_clean_text(notes) or normalized.notes,
        )

    def build_courier_event_doc(
        self,
        event: Mapping[str, Any] | CourierEvent | CourierEventDraft,
        *,
        notes: str = "",
    ) -> CourierEventDraft:
        """Return one normalized courier event draft."""

        normalized = _normalize_courier_event(
            event,
            courier_name=self.courier_name,
        )
        shipment = _normalize_courier_shipment(
            {
                "shipment_id": normalized.shipment_id,
                "order_id": normalized.shipment_id,
                "courier_name": normalized.courier_name,
                "service_mode": "Address Delivery",
                "destination_country": "BG",
                "shipment_state": "Draft",
                "label_reference": normalized.label_reference,
                "tracking_number": normalized.tracking_number,
                "notes": normalized.notes,
            },
            courier_name=normalized.courier_name,
        )
        blockers = _shipment_validation_blockers(shipment, adapter=self)
        review_required = normalized.event_state == "Review" or bool(blockers)
        return CourierEventDraft(
            event_id=normalized.event_id,
            shipment_id=normalized.shipment_id,
            courier_name=normalized.courier_name,
            event_type=normalized.event_type,
            occurred_at=normalized.occurred_at,
            event_state=normalized.event_state,
            tracking_number=normalized.tracking_number,
            label_reference=normalized.label_reference,
            notes=_clean_text(notes) or normalized.notes,
            review_required=review_required,
            validation_blockers=blockers,
        )

    def build_courier_dispatch_batch_doc(
        self,
        *,
        batch_id: str,
        shipments: Iterable[
            Mapping[str, Any] | CourierShipment | CourierShipmentDraft
        ],
        events: Iterable[
            Mapping[str, Any] | CourierEvent | CourierEventDraft
        ] = (),
        status: str = "",
        notes: str = "",
    ) -> CourierDispatchBatchDraft:
        """Return one normalized courier dispatch batch draft."""

        shipment_drafts = tuple(
            self.build_courier_shipment_doc(shipment) for shipment in shipments
        )
        event_drafts = tuple(
            self.build_courier_event_doc(event) for event in events
        )
        if not event_drafts:
            generated_events = []
            for index, shipment_draft in enumerate(shipment_drafts, start=1):
                tracking_reference = shipment_draft.tracking_reference
                generated_events.append(
                    self.build_courier_event_doc(
                        {
                            "event_id": f"{batch_id}-{index}",
                            "shipment_id": shipment_draft.shipment_id,
                            "courier_name": shipment_draft.courier_name,
                            "event_type": _derive_event_type(
                                shipment_draft.to_contract(),
                                shipment_draft.validation_blockers,
                            ),
                            "occurred_at": (
                                tracking_reference.captured_at
                                if tracking_reference is not None
                                and tracking_reference.captured_at
                                else shipment_draft.shipment_state
                            ),
                            "event_state": _derive_event_state(
                                shipment_draft.to_contract(),
                                shipment_draft.validation_blockers,
                            ),
                            "tracking_number": shipment_draft.tracking_number,
                            "label_reference": shipment_draft.label_reference,
                            "notes": shipment_draft.notes,
                        },
                        notes=shipment_draft.notes,
                    )
                )
            event_drafts = tuple(generated_events)
        validation_blockers = tuple(
            blocker
            for shipment in shipment_drafts
            for blocker in shipment.validation_blockers
        )
        selected_status = _derive_batch_status(
            shipment_drafts,
            event_drafts,
            _clean_text(status),
        )
        review_required = (
            bool(validation_blockers)
            or any(draft.review_required for draft in shipment_drafts)
            or any(event.review_required for event in event_drafts)
        )
        if not batch_id:
            raise ValueError("batch_id is required")
        return CourierDispatchBatchDraft(
            batch_id=_clean_text(batch_id),
            courier_name=self.courier_name,
            status=selected_status,
            notes=_clean_text(notes),
            shipments=shipment_drafts,
            events=event_drafts,
            review_required=review_required,
            validation_blockers=validation_blockers,
        )

    def build_courier_summary_doc(
        self,
        batch: CourierDispatchBatchDraft,
    ) -> CourierSummaryDraft:
        """Return one normalized courier summary draft."""

        contract_summary = build_courier_summary(batch.to_contract())
        operator_state = _derive_operator_state(
            batch.validation_blockers,
            contract_summary.review_required,
            batch.status,
        )
        return CourierSummaryDraft(
            batch_id=contract_summary.batch_id,
            courier_name=contract_summary.courier_name,
            shipment_count=contract_summary.shipment_count,
            event_count=contract_summary.event_count,
            tracking_count=contract_summary.tracking_count,
            cod_pending_count=contract_summary.cod_pending_count,
            return_count=contract_summary.return_count,
            exception_count=contract_summary.exception_count,
            review_required=contract_summary.review_required,
            operator_state=operator_state,
            notes=batch.notes,
        )


class CourierSimulatorAdapter(_CourierAdapterBase):
    """Describe the local courier simulator adapter shell."""

    def __init__(self, courier_name: str = "Speedy") -> None:
        """Build a simulator shell for the selected courier."""

        normalized = _normalize_courier_name(courier_name) or "Speedy"
        capabilities = _simulator_capabilities(normalized)
        super().__init__(
            courier_name=normalized,
            capabilities=capabilities,
            adapter_name="Courier Simulator",
        )

    def sample_shipments(self) -> tuple[CourierShipment, ...]:
        """Return sample shipments for proof and smoke tests."""

        if self.courier_name == "Econt":
            return (
                CourierShipment(
                    shipment_id="SHIP-2026-0001",
                    order_id="SO-2026-0001",
                    courier_name="Econt",
                    service_mode="Address Delivery",
                    destination_country="BG",
                    shipment_state="Delivered",
                    label_reference="LBL-2026-0001",
                    tracking_number="TRK-2026-0001",
                    cod_state="Collected",
                    payout_state="Pending",
                    return_state="None",
                ),
                CourierShipment(
                    shipment_id="SHIP-2026-0002",
                    order_id="SO-2026-0002",
                    courier_name="Econt",
                    service_mode="Office Pickup",
                    destination_country="BG",
                    shipment_state="Returned",
                    label_reference="LBL-2026-0002",
                    tracking_number="TRK-2026-0002",
                    cod_state="Pending",
                    payout_state="Settled",
                    return_state="Returned",
                    exception_state="requires_review",
                ),
            )
        return (
            CourierShipment(
                shipment_id="SHIP-2026-0001",
                order_id="SO-2026-0001",
                courier_name="Speedy",
                service_mode="Address Delivery",
                destination_country="BG",
                shipment_state="Delivered",
                label_reference="LBL-2026-0001",
                tracking_number="TRK-2026-0001",
                cod_state="Collected",
                payout_state="Pending",
                return_state="None",
            ),
            CourierShipment(
                shipment_id="SHIP-2026-0002",
                order_id="SO-2026-0002",
                courier_name="Speedy",
                service_mode="Office Pickup",
                destination_country="BG",
                shipment_state="Returned",
                label_reference="LBL-2026-0002",
                tracking_number="TRK-2026-0002",
                cod_state="Pending",
                payout_state="Settled",
                return_state="Returned",
                exception_state="requires_review",
            ),
        )


class CourierSpeedyAdapter(_CourierAdapterBase):
    """Describe the Speedy adapter shell."""

    def __init__(self) -> None:
        """Build the default Speedy capability profile."""

        super().__init__(
            courier_name="Speedy",
            capabilities=_simulator_capabilities("Speedy"),
            adapter_name="Speedy Adapter",
        )


class CourierEcontAdapter(_CourierAdapterBase):
    """Describe the Econt adapter shell."""

    def __init__(self) -> None:
        """Build the default Econt capability profile."""

        super().__init__(
            courier_name="Econt",
            capabilities=_simulator_capabilities("Econt"),
            adapter_name="Econt Adapter",
        )


def _simulator_capabilities(courier_name: str) -> CourierCapability:
    """Return the shell capability matrix for one courier."""

    normalized = _normalize_courier_name(courier_name)
    if normalized == "Speedy":
        return CourierCapability(
            courier_name="Speedy",
            supports_domestic=True,
            supports_international=True,
            supports_office_pickup=True,
            supports_address_delivery=True,
            supports_store_pickup=False,
            supports_cod=True,
            supports_label_creation=True,
            supports_tracking=True,
            supports_pickup_requests=True,
            supports_returns=True,
        )
    if normalized == "Econt":
        return CourierCapability(
            courier_name="Econt",
            supports_domestic=True,
            supports_international=False,
            supports_office_pickup=True,
            supports_address_delivery=True,
            supports_store_pickup=False,
            supports_cod=True,
            supports_label_creation=True,
            supports_tracking=True,
            supports_pickup_requests=True,
            supports_returns=True,
        )
    raise ValueError(f"unsupported courier adapter: {courier_name!r}")


DEFAULT_COURIER_ADAPTERS: tuple[_CourierAdapterBase, ...] = (
    CourierSpeedyAdapter(),
    CourierEcontAdapter(),
)


def select_courier_adapters(
    destination_country: str,
    service_mode: str,
    *,
    requires_cod: bool = False,
    adapters: Iterable[_CourierAdapterBase] | None = None,
) -> tuple[_CourierAdapterBase, ...]:
    """Return the adapters that can serve the requested shipment."""

    available_adapters = (
        tuple(adapters) if adapters is not None else DEFAULT_COURIER_ADAPTERS
    )
    return tuple(
        adapter
        for adapter in available_adapters
        if adapter.supports_order(
            destination_country,
            service_mode,
            requires_cod=requires_cod,
        )
    )


def shipment_validation_blockers(
    shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
    *,
    courier_name: str = "",
    adapter: CourierAdapter | None = None,
) -> tuple[str, ...]:
    """Return the structural shipment blockers for one shipment."""

    normalized = _normalize_courier_shipment(
        shipment,
        courier_name=courier_name,
    )
    return _shipment_validation_blockers(normalized, adapter=adapter)


def validate_courier_shipment(
    shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
    *,
    courier_name: str = "",
    adapter: CourierAdapter | None = None,
) -> bool:
    """Return whether one shipment is structurally valid."""

    return not shipment_validation_blockers(
        shipment,
        courier_name=courier_name,
        adapter=adapter,
    )


def build_courier_shipment_doc(
    shipment: Mapping[str, Any] | CourierShipment | CourierShipmentDraft,
    *,
    courier_name: str = "",
    notes: str = "",
) -> CourierShipmentDraft:
    """Build one normalized courier shipment draft."""
    normalized = _normalize_courier_shipment(
        shipment,
        courier_name=(
            courier_name
            or _clean_text(_mapping_from_input(shipment).get("courier_name"))
        ),
    )
    adapter = CourierSimulatorAdapter(normalized.courier_name or "Speedy")
    draft = adapter.build_courier_shipment_doc(normalized, notes=notes)
    return draft


def build_courier_event_doc(
    event: Mapping[str, Any] | CourierEvent | CourierEventDraft,
    *,
    courier_name: str = "",
    notes: str = "",
) -> CourierEventDraft:
    """Build one normalized courier event draft."""

    normalized = _normalize_courier_event(
        event,
        courier_name=courier_name,
    )
    adapter = CourierSimulatorAdapter(normalized.courier_name or "Speedy")
    return adapter.build_courier_event_doc(normalized, notes=notes)


def build_courier_dispatch_batch_doc(
    *,
    batch_id: str,
    shipments: Iterable[
        Mapping[str, Any] | CourierShipment | CourierShipmentDraft
    ],
    courier_name: str = "",
    events: Iterable[
        Mapping[str, Any] | CourierEvent | CourierEventDraft
    ] = (),
    status: str = "",
    notes: str = "",
) -> CourierDispatchBatchDraft:
    """Build one courier dispatch batch draft."""

    normalized_shipments = tuple(
        _normalize_courier_shipment(
            shipment,
            courier_name=courier_name,
        )
        for shipment in shipments
    )
    adapter_name = _normalize_courier_name(courier_name) or (
        normalized_shipments[0].courier_name
        if normalized_shipments
        else "Speedy"
    )
    adapter = CourierSimulatorAdapter(adapter_name)
    return adapter.build_courier_dispatch_batch_doc(
        batch_id=batch_id,
        shipments=normalized_shipments,
        events=tuple(events),
        status=status,
        notes=notes,
    )


def build_courier_summary_doc(
    batch: CourierDispatchBatchDraft,
) -> CourierSummaryDraft:
    """Build one courier summary draft."""

    adapter = CourierSimulatorAdapter(batch.courier_name or "Speedy")
    return adapter.build_courier_summary_doc(batch)


__all__ = [
    "COURIER_EVENT_TYPES",
    "DEFAULT_COURIER_ADAPTERS",
    "DEFAULT_COURIER_TARGETS",
    "CourierAdapter",
    "CourierDispatchBatchDraft",
    "CourierEcontAdapter",
    "CourierEventDraft",
    "CourierShipmentDraft",
    "CourierSimulatorAdapter",
    "CourierSpeedyAdapter",
    "CourierSummaryDraft",
    "CourierTrackingReferenceDraft",
    "build_courier_dispatch_batch_doc",
    "build_courier_event_doc",
    "build_courier_shipment_doc",
    "build_courier_summary_doc",
    "select_courier_adapters",
    "shipment_validation_blockers",
    "validate_courier_shipment",
]
