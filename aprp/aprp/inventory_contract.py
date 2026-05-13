"""Core APRP inventory, packaging, and location-policy contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

PACK_ROLES: Final[tuple[str, ...]] = ("Unit", "Box", "Case")
WAREHOUSE_PURPOSES: Final[tuple[str, ...]] = (
    "Fulfillment",
    "Reserve",
    "Intake",
)
STOCK_OPERATIONS: Final[tuple[str, ...]] = (
    "move",
    "transfer",
    "count",
    "reserve",
)


@dataclass(frozen=True)
class PackFamily:
    """Describe one pack family across unit, box, and case tiers."""

    name: str
    unit_item: str
    box_item: str | None = None
    case_item: str | None = None
    units_per_box: int | None = None
    boxes_per_case: int | None = None
    notes: str = ""

    def pack_roles(self) -> tuple[str, ...]:
        """Return the pack roles that this family currently exposes."""

        roles = ["Unit"]
        if self.box_item is not None:
            roles.append("Box")
        if self.case_item is not None:
            roles.append("Case")
        return tuple(roles)

    def units_for(self, pack_role: str, quantity: int) -> int:
        """Convert a pack quantity into unit quantity."""

        if quantity < 0:
            raise ValueError("quantity must be non-negative")

        if pack_role == "Unit":
            return quantity
        if pack_role == "Box":
            if self.units_per_box is None:
                raise ValueError("units_per_box is required for box counts")
            return quantity * self.units_per_box
        if pack_role == "Case":
            if self.units_per_box is None or self.boxes_per_case is None:
                raise ValueError(
                    "units_per_box and boxes_per_case are required for "
                    "case counts"
                )
            return quantity * self.units_per_box * self.boxes_per_case
        raise ValueError(f"unsupported pack role: {pack_role}")

    def has_sealed_tier(self, pack_role: str) -> bool:
        """Return whether the family exposes the requested sealed tier."""

        return pack_role in self.pack_roles()


@dataclass(frozen=True)
class WarehousePolicy:
    """Describe one location-purpose warehouse policy row."""

    policy_name: str
    location: str
    warehouse: str
    purpose: str
    priority: int = 0
    web_buffer: float = 0.0
    active: bool = True
    notes: str = ""

    def applies_to(self, location: str, purpose: str) -> bool:
        """Return whether this policy matches the requested route."""

        return (
            self.active
            and self.location == location
            and self.purpose == purpose
        )


@dataclass(frozen=True)
class WarehousePolicySet:
    """Resolve explicit fulfillment, reserve, and intake warehouses."""

    policies: tuple[WarehousePolicy, ...] = ()

    def policies_for(self, location: str) -> tuple[WarehousePolicy, ...]:
        """Return the policies configured for one location."""

        return tuple(
            policy
            for policy in self.policies
            if policy.active and policy.location == location
        )

    def resolve(self, location: str, purpose: str) -> WarehousePolicy | None:
        """Return the highest-priority policy for one location-purpose pair."""

        candidates = [
            policy
            for policy in self.policies
            if policy.applies_to(location, purpose)
        ]
        if not candidates:
            return None
        return sorted(candidates, key=lambda policy: policy.priority)[0]

    def warehouse_for(self, location: str, purpose: str) -> str | None:
        """Return the warehouse selected for one location-purpose pair."""

        policy = self.resolve(location, purpose)
        return None if policy is None else policy.warehouse


@dataclass(frozen=True)
class IntakeLine:
    """Describe one barcode-first intake line."""

    supplier_sku: str
    raw_name: str
    barcode: str | None = None
    item: str | None = None
    invoice_line_number: str | None = None
    quantity: float = 1
    pack_role: str = "Unit"
    confirmed: bool = False
    notes: str = ""

    def is_ready(self) -> bool:
        """Return whether the line can be posted into stock."""

        return self.confirmed and self.quantity > 0 and bool(self.supplier_sku)


@dataclass(frozen=True)
class IntakeSession:
    """Describe one barcode-driven stock intake session."""

    session_id: str
    warehouse: str
    posting_date: str
    operator: str | None = None
    confirm_scanned_quantities: bool = False
    confirm_ready_to_post: bool = False
    notes: str = ""
    lines: tuple[IntakeLine, ...] = ()

    def ready_lines(self) -> tuple[IntakeLine, ...]:
        """Return the lines that are individually ready for posting."""

        return tuple(line for line in self.lines if line.is_ready())

    def is_ready_to_post(self) -> bool:
        """Return whether the session can post stock."""

        if not (
            self.confirm_scanned_quantities and self.confirm_ready_to_post
        ):
            return False
        return len(self.lines) > 0 and all(
            line.is_ready() for line in self.lines
        )


@dataclass(frozen=True)
class UnresolvedBarcode:
    """Describe one barcode that still needs mapping."""

    barcode: str
    warehouse: str
    status: str = "Open"
    resolved_item: str | None = None
    resolved_pack_role: str | None = None
    notes: str = ""

    def is_resolved(self) -> bool:
        """Return whether the barcode has been mapped to a known item."""

        return self.status == "Resolved" or self.resolved_item is not None


@dataclass(frozen=True)
class StockOperation:
    """Describe a stock move, transfer, count, or reservation event."""

    operation: str
    item: str
    quantity: float
    source_warehouse: str | None = None
    target_warehouse: str | None = None
    location: str | None = None
    reference: str | None = None
    notes: str = ""

    def requires_source(self) -> bool:
        """Return whether the operation needs a source warehouse."""

        return self.operation in {"move", "transfer"}

    def requires_target(self) -> bool:
        """Return whether the operation needs a target warehouse."""

        return self.operation in {"move", "transfer", "reserve"}


@dataclass(frozen=True)
class InventorySafetyGate:
    """Describe the minimum inventory facts required to sell or publish."""

    stock_known: bool
    stock_consistent: bool
    pack_family_known: bool
    policy_resolved: bool
    reservation_state_known: bool = True

    def can_sell(self) -> bool:
        """Return whether the stock data is safe enough to sell."""

        return all(
            [
                self.stock_known,
                self.stock_consistent,
                self.pack_family_known,
                self.policy_resolved,
                self.reservation_state_known,
            ]
        )

    def can_publish(self) -> bool:
        """Return whether the stock data is safe enough to publish."""

        return self.can_sell()

    def missing_requirements(self) -> tuple[str, ...]:
        """Return the missing requirements that block selling or publishing."""

        missing = []
        if not self.stock_known:
            missing.append("stock_known")
        if not self.stock_consistent:
            missing.append("stock_consistent")
        if not self.pack_family_known:
            missing.append("pack_family_known")
        if not self.policy_resolved:
            missing.append("policy_resolved")
        if not self.reservation_state_known:
            missing.append("reservation_state_known")
        return tuple(missing)


__all__ = [
    "IntakeLine",
    "IntakeSession",
    "InventorySafetyGate",
    "PACK_ROLES",
    "PackFamily",
    "STOCK_OPERATIONS",
    "StockOperation",
    "UnresolvedBarcode",
    "WAREHOUSE_PURPOSES",
    "WarehousePolicy",
    "WarehousePolicySet",
]
