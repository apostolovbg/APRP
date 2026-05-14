"""APRP runtime service helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, is_dataclass, replace
from typing import Any, Mapping

from .inventory_contract import PACK_ROLES
from .inventory_contract import IntakeLine as ContractIntakeLine
from .inventory_contract import IntakeSession as ContractIntakeSession
from .inventory_contract import InventorySafetyGate


def _clean_text(value: Any) -> str:
    """Return a stripped string representation for a runtime field."""

    if value is None:
        return ""
    return str(value).strip()


def _coerce_bool(value: Any) -> bool:
    """Return a stable boolean representation for runtime inputs."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _coerce_float(value: Any) -> float:
    """Return a float representation for runtime quantity inputs."""

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
    raise TypeError(f"unsupported runtime service input: {type(value)!r}")


def _canonical_payload(payload: Any) -> bytes:
    """Return a canonical JSON representation for payload hashing."""

    payload_text = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return payload_text.encode("utf-8")


def _payload_hash(payload: Any) -> str:
    """Return the stable payload hash for integration log rows."""

    if payload is None:
        return ""
    return hashlib.sha256(_canonical_payload(payload)).hexdigest()


def _status_from_parts(
    confirm_scanned_quantities: bool,
    confirm_ready_to_post: bool,
    lines: tuple["IntakeLineDraft", ...],
) -> str:
    """Return the most accurate intake status for the current draft."""

    if not lines:
        return "Draft"
    if (
        confirm_scanned_quantities
        and confirm_ready_to_post
        and all(line.is_ready() for line in lines)
    ):
        return "Ready"
    return "In Progress"


@dataclass(frozen=True)
class ProductProfileDraft:
    """Describe one product profile draft for APRP."""

    profile_name: str = ""
    product: str = ""
    supplier: str = ""
    tax_profile: str = ""
    price_list: str = ""
    barcode: str = ""
    description: str = ""
    publishable: bool = False
    notes: str = ""

    @classmethod
    def from_input(
        cls,
        value: Mapping[str, Any] | "ProductProfileDraft" | None = None,
        **changes: Any,
    ) -> "ProductProfileDraft":
        """Build a normalized profile draft from input data."""

        profile_data = _mapping_from_input(value)
        profile_data.update(changes)
        return cls(
            profile_name=_clean_text(profile_data.get("profile_name")),
            product=_clean_text(profile_data.get("product")),
            supplier=_clean_text(profile_data.get("supplier")),
            tax_profile=_clean_text(profile_data.get("tax_profile")),
            price_list=_clean_text(profile_data.get("price_list")),
            barcode=_clean_text(profile_data.get("barcode")),
            description=_clean_text(profile_data.get("description")),
            publishable=_coerce_bool(profile_data.get("publishable")),
            notes=_clean_text(profile_data.get("notes")),
        )

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this profile draft."""

        return {
            "profile_name": self.profile_name,
            "product": self.product,
            "supplier": self.supplier,
            "tax_profile": self.tax_profile,
            "price_list": self.price_list,
            "barcode": self.barcode,
            "description": self.description,
            "publishable": self.publishable,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class SupplierSkuMappingDraft:
    """Describe one supplier SKU mapping draft for APRP."""

    supplier: str = ""
    product: str = ""
    sku: str = ""
    barcode: str = ""
    notes: str = ""

    @classmethod
    def from_input(
        cls,
        value: Mapping[str, Any] | "SupplierSkuMappingDraft" | None = None,
        **changes: Any,
    ) -> "SupplierSkuMappingDraft":
        """Build a normalized supplier mapping from input data."""

        mapping_data = _mapping_from_input(value)
        mapping_data.update(changes)
        return cls(
            supplier=_clean_text(mapping_data.get("supplier")),
            product=_clean_text(mapping_data.get("product")),
            sku=_clean_text(mapping_data.get("sku")),
            barcode=_clean_text(mapping_data.get("barcode")),
            notes=_clean_text(mapping_data.get("notes")),
        )

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this mapping draft."""

        return {
            "supplier": self.supplier,
            "product": self.product,
            "sku": self.sku,
            "barcode": self.barcode,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class IntakeLineDraft:
    """Describe one barcode-first intake line draft for APRP."""

    supplier_sku: str = ""
    raw_name: str = ""
    barcode: str = ""
    product: str = ""
    invoice_line_number: str = ""
    quantity: float = 1.0
    pack_role: str = "Unit"
    confirmed: bool = False
    notes: str = ""

    @classmethod
    def from_input(
        cls,
        value: (
            Mapping[str, Any] | ContractIntakeLine | "IntakeLineDraft" | None
        ) = None,
        **changes: Any,
    ) -> "IntakeLineDraft":
        """Build a normalized intake line from contract or doc data."""

        if isinstance(value, ContractIntakeLine):
            line_data: dict[str, Any] = {
                "supplier_sku": value.supplier_sku,
                "raw_name": value.raw_name,
                "barcode": value.barcode or "",
                "product": value.item or "",
                "invoice_line_number": value.invoice_line_number or "",
                "quantity": value.quantity,
                "pack_role": value.pack_role,
                "confirmed": value.confirmed,
                "notes": value.notes,
            }
        else:
            line_data = _mapping_from_input(value)
            if "product" not in line_data and "item" in line_data:
                line_data["product"] = line_data["item"]
        line_data.update(changes)
        return cls(
            supplier_sku=_clean_text(line_data.get("supplier_sku")),
            raw_name=_clean_text(line_data.get("raw_name")),
            barcode=_clean_text(line_data.get("barcode")),
            product=_clean_text(line_data.get("product")),
            invoice_line_number=_clean_text(
                line_data.get("invoice_line_number")
            ),
            quantity=_coerce_float(line_data.get("quantity", 1.0)),
            pack_role=_clean_text(line_data.get("pack_role")) or "Unit",
            confirmed=_coerce_bool(line_data.get("confirmed")),
            notes=_clean_text(line_data.get("notes")),
        )

    def blockers(self) -> tuple[str, ...]:
        """Return the missing fields that block a safe intake post."""

        blockers = []
        if not self.supplier_sku:
            blockers.append("supplier_sku")
        if not self.raw_name:
            blockers.append("raw_name")
        if not self.product:
            blockers.append("product")
        if self.quantity <= 0:
            blockers.append("quantity")
        if self.pack_role not in PACK_ROLES:
            blockers.append("pack_role")
        if not self.confirmed:
            blockers.append("confirmed")
        return tuple(blockers)

    def is_ready(self) -> bool:
        """Return whether the line can be posted into stock."""

        return len(self.blockers()) == 0

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this intake line."""

        return {
            "supplier_sku": self.supplier_sku,
            "raw_name": self.raw_name,
            "barcode": self.barcode,
            "product": self.product,
            "invoice_line_number": self.invoice_line_number,
            "quantity": self.quantity,
            "pack_role": self.pack_role,
            "confirmed": self.confirmed,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class IntakeSessionDraft:
    """Describe one barcode-driven intake session draft for APRP."""

    naming_series: str = "INTAKE-.YYYY.-.####"
    expense_id: str = ""
    status: str = "Draft"
    posting_date: str = ""
    location: str = ""
    warehouse: str = ""
    supplier: str = ""
    operator: str = ""
    confirm_scanned_quantities: bool = False
    confirm_ready_to_post: bool = False
    notes: str = ""
    lines: tuple[IntakeLineDraft, ...] = ()

    @classmethod
    def from_input(
        cls,
        value: (
            Mapping[str, Any]
            | ContractIntakeSession
            | "IntakeSessionDraft"
            | None
        ) = None,
        **changes: Any,
    ) -> "IntakeSessionDraft":
        """Build a normalized intake session from contract or doc data."""

        if isinstance(value, ContractIntakeSession):
            session_data: dict[str, Any] = {
                "naming_series": "INTAKE-.YYYY.-.####",
                "expense_id": value.session_id,
                "status": "",
                "posting_date": value.posting_date,
                "location": "",
                "warehouse": value.warehouse,
                "supplier": "",
                "operator": value.operator or "",
                "confirm_scanned_quantities": value.confirm_scanned_quantities,
                "confirm_ready_to_post": value.confirm_ready_to_post,
                "notes": value.notes,
                "lines": tuple(
                    IntakeLineDraft.from_input(line) for line in value.lines
                ),
            }
        else:
            session_data = _mapping_from_input(value)
        session_data.update(changes)
        raw_lines = session_data.get("lines", ())
        lines = tuple(IntakeLineDraft.from_input(line) for line in raw_lines)
        status = _clean_text(session_data.get("status"))
        if not status:
            status = _status_from_parts(
                _coerce_bool(session_data.get("confirm_scanned_quantities")),
                _coerce_bool(session_data.get("confirm_ready_to_post")),
                lines,
            )
        return cls(
            naming_series=_clean_text(session_data.get("naming_series"))
            or "INTAKE-.YYYY.-.####",
            expense_id=_clean_text(session_data.get("expense_id")),
            status=status,
            posting_date=_clean_text(session_data.get("posting_date")),
            location=_clean_text(session_data.get("location")),
            warehouse=_clean_text(session_data.get("warehouse")),
            supplier=_clean_text(session_data.get("supplier")),
            operator=_clean_text(session_data.get("operator")),
            confirm_scanned_quantities=_coerce_bool(
                session_data.get("confirm_scanned_quantities")
            ),
            confirm_ready_to_post=_coerce_bool(
                session_data.get("confirm_ready_to_post")
            ),
            notes=_clean_text(session_data.get("notes")),
            lines=lines,
        )

    def line_count(self) -> int:
        """Return the number of lines in the intake session."""

        return len(self.lines)

    def ready_line_count(self) -> int:
        """Return the number of ready lines in the intake session."""

        return sum(1 for line in self.lines if line.is_ready())

    def is_ready_to_post(self) -> bool:
        """Return whether the session can move into posting."""

        if self.status in {"Posted", "Cancelled"}:
            return False
        return (
            self.line_count() > 0
            and self.confirm_scanned_quantities
            and self.confirm_ready_to_post
            and self.ready_line_count() == self.line_count()
        )

    def with_line(
        self,
        line: Mapping[str, Any] | ContractIntakeLine | IntakeLineDraft,
    ) -> "IntakeSessionDraft":
        """Return a new session draft with one more normalized line."""

        if self.status in {"Posted", "Cancelled"}:
            raise ValueError("cannot add lines to a closed intake session")
        updated = replace(
            self,
            lines=self.lines + (IntakeLineDraft.from_input(line),),
        )
        if updated.is_ready_to_post():
            return replace(updated, status="Ready")
        return replace(updated, status="In Progress")

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this intake session."""

        return {
            "naming_series": self.naming_series,
            "expense_id": self.expense_id,
            "status": self.status,
            "posting_date": self.posting_date,
            "location": self.location,
            "warehouse": self.warehouse,
            "supplier": self.supplier,
            "operator": self.operator,
            "confirm_scanned_quantities": self.confirm_scanned_quantities,
            "confirm_ready_to_post": self.confirm_ready_to_post,
            "notes": self.notes,
            "lines": [line.to_doc() for line in self.lines],
        }


@dataclass(frozen=True)
class UnresolvedBarcodeDraft:
    """Describe one unresolved barcode draft for APRP."""

    naming_series: str = "UNRES-.YYYY.-.####"
    status: str = "Open"
    barcode: str = ""
    quantity: float = 1.0
    location: str = ""
    warehouse: str = ""
    reason: str = "Unknown"
    resolved_product: str = ""
    resolved_by: str = ""
    resolved_on: str = ""
    pack_family_draft: str = ""

    def is_resolved(self) -> bool:
        """Return whether the barcode draft already has a resolution."""

        return self.status == "Resolved" or bool(self.resolved_product)

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this barcode draft."""

        return {
            "naming_series": self.naming_series,
            "status": self.status,
            "barcode": self.barcode,
            "quantity": self.quantity,
            "location": self.location,
            "warehouse": self.warehouse,
            "reason": self.reason,
            "resolved_product": self.resolved_product,
            "resolved_by": self.resolved_by,
            "resolved_on": self.resolved_on,
            "pack_family_draft": self.pack_family_draft,
        }


@dataclass(frozen=True)
class IntegrationLogEntryDraft:
    """Describe one integration log entry draft for APRP."""

    integration_name: str = ""
    operation: str = ""
    direction: str = "Inbound"
    reference_doctype: str = ""
    reference_name: str = ""
    status: str = "Pending"
    message: str = ""
    payload_hash: str = ""
    notes: str = ""
    payload: Mapping[str, Any] | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        """Populate the payload hash when a payload is present."""

        if self.payload is not None and not self.payload_hash:
            object.__setattr__(
                self, "payload_hash", _payload_hash(self.payload)
            )

    @classmethod
    def from_input(
        cls,
        value: Mapping[str, Any] | "IntegrationLogEntryDraft" | None = None,
        **changes: Any,
    ) -> "IntegrationLogEntryDraft":
        """Build a normalized integration log entry from input data."""

        log_data = _mapping_from_input(value)
        log_data.update(changes)
        return cls(
            integration_name=_clean_text(log_data.get("integration_name")),
            operation=_clean_text(log_data.get("operation")),
            direction=_clean_text(log_data.get("direction")) or "Inbound",
            reference_doctype=_clean_text(log_data.get("reference_doctype")),
            reference_name=_clean_text(log_data.get("reference_name")),
            status=_clean_text(log_data.get("status")) or "Pending",
            message=_clean_text(log_data.get("message")),
            payload_hash=_clean_text(log_data.get("payload_hash")),
            notes=_clean_text(log_data.get("notes")),
            payload=log_data.get("payload"),
        )

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped payload for this log entry."""

        return {
            "integration_name": self.integration_name,
            "operation": self.operation,
            "direction": self.direction,
            "reference_doctype": self.reference_doctype,
            "reference_name": self.reference_name,
            "status": self.status,
            "message": self.message,
            "payload_hash": self.payload_hash,
            "notes": self.notes,
        }


def product_publishability_blockers(
    profile: Mapping[str, Any] | ProductProfileDraft | None = None,
    *,
    safety_gate: InventorySafetyGate | None = None,
    **changes: Any,
) -> tuple[str, ...]:
    """Return the blockers that prevent a product from being publishable."""

    draft = ProductProfileDraft.from_input(profile, **changes)
    blockers = []
    if not draft.profile_name:
        blockers.append("profile_name")
    if not draft.product:
        blockers.append("product")
    if not draft.supplier:
        blockers.append("supplier")
    if not draft.tax_profile:
        blockers.append("tax_profile")
    if not draft.price_list:
        blockers.append("price_list")
    if not draft.barcode:
        blockers.append("barcode")
    if not draft.publishable:
        blockers.append("publishable")
    if safety_gate is not None and not safety_gate.can_publish():
        blockers.extend(safety_gate.missing_requirements())
    return tuple(blockers)


def validate_product_publishability(
    profile: Mapping[str, Any] | ProductProfileDraft | None = None,
    *,
    safety_gate: InventorySafetyGate | None = None,
    **changes: Any,
) -> bool:
    """Return whether the profile is safe to publish."""

    return (
        len(
            product_publishability_blockers(
                profile,
                safety_gate=safety_gate,
                **changes,
            )
        )
        == 0
    )


def build_product_profile_doc(
    profile: Mapping[str, Any] | ProductProfileDraft | None = None,
    *,
    safety_gate: InventorySafetyGate | None = None,
    **changes: Any,
) -> dict[str, Any]:
    """Return a DocType-shaped product profile payload."""

    draft = ProductProfileDraft.from_input(profile, **changes)
    publishable = validate_product_publishability(
        draft,
        safety_gate=safety_gate,
    )
    return replace(draft, publishable=publishable).to_doc()


def build_supplier_sku_mapping_doc(
    mapping: Mapping[str, Any] | SupplierSkuMappingDraft | None = None,
    **changes: Any,
) -> dict[str, Any]:
    """Return a DocType-shaped supplier SKU mapping payload."""

    return SupplierSkuMappingDraft.from_input(mapping, **changes).to_doc()


def open_intake_session(
    *,
    expense_id: str,
    warehouse: str,
    posting_date: str,
    location: str = "",
    supplier: str = "",
    operator: str = "",
    naming_series: str = "INTAKE-.YYYY.-.####",
    confirm_scanned_quantities: bool = False,
    confirm_ready_to_post: bool = False,
    notes: str = "",
) -> IntakeSessionDraft:
    """Return a fresh intake session draft with a Draft status."""

    return IntakeSessionDraft(
        naming_series=naming_series,
        expense_id=expense_id,
        status="Draft",
        posting_date=posting_date,
        location=location,
        warehouse=warehouse,
        supplier=supplier,
        operator=operator,
        confirm_scanned_quantities=confirm_scanned_quantities,
        confirm_ready_to_post=confirm_ready_to_post,
        notes=notes,
    )


def add_intake_line(
    session: Mapping[str, Any] | ContractIntakeSession | IntakeSessionDraft,
    line: Mapping[str, Any] | ContractIntakeLine | IntakeLineDraft,
) -> IntakeSessionDraft:
    """Return a new intake session draft with one extra normalized line."""

    draft = IntakeSessionDraft.from_input(session)
    return draft.with_line(line)


def intake_session_blockers(
    session: Mapping[str, Any] | ContractIntakeSession | IntakeSessionDraft,
) -> tuple[str, ...]:
    """Return the blockers that keep an intake session from posting."""

    draft = IntakeSessionDraft.from_input(session)
    blockers = []
    if draft.status in {"Posted", "Cancelled"}:
        blockers.append("session_closed")
    if not draft.lines:
        blockers.append("lines")
    if not draft.confirm_scanned_quantities:
        blockers.append("confirm_scanned_quantities")
    if not draft.confirm_ready_to_post:
        blockers.append("confirm_ready_to_post")
    for line in draft.lines:
        key = line.supplier_sku or line.raw_name or "line"
        for blocker in line.blockers():
            blockers.append(f"{key}:{blocker}")
    return tuple(blockers)


def post_safe_intake_session(
    session: Mapping[str, Any] | ContractIntakeSession | IntakeSessionDraft,
) -> IntakeSessionDraft:
    """Return a posted intake session when no blockers remain."""

    draft = IntakeSessionDraft.from_input(session)
    if draft.status in {"Posted", "Cancelled"}:
        raise ValueError("cannot post a closed intake session")
    blockers = intake_session_blockers(draft)
    if blockers:
        raise ValueError("unsafe intake session: " + ", ".join(blockers))
    return replace(draft, status="Posted")


def block_unsafe_intake_session(
    session: Mapping[str, Any] | ContractIntakeSession | IntakeSessionDraft,
) -> IntakeSessionDraft:
    """Return a cancelled intake session that records its blockers."""

    draft = IntakeSessionDraft.from_input(session)
    if draft.status in {"Posted", "Cancelled"}:
        raise ValueError("cannot block a closed intake session")
    blockers = intake_session_blockers(draft)
    if not blockers:
        raise ValueError("session is safe to post")
    notes = draft.notes
    blocker_note = "Blocked: " + ", ".join(blockers)
    if notes:
        notes = f"{notes} | {blocker_note}"
    else:
        notes = blocker_note
    return replace(draft, status="Cancelled", notes=notes)


def detect_unresolved_barcode(
    line: Mapping[str, Any] | ContractIntakeLine | IntakeLineDraft,
    *,
    location: str = "",
    warehouse: str = "",
) -> UnresolvedBarcodeDraft | None:
    """Return an unresolved barcode draft when the intake line is unmapped."""

    draft = IntakeLineDraft.from_input(line)
    if not draft.barcode or draft.product:
        return None
    return UnresolvedBarcodeDraft(
        barcode=draft.barcode,
        quantity=draft.quantity,
        location=_clean_text(location),
        warehouse=_clean_text(warehouse),
        reason="Unknown",
    )


def build_integration_log_entry(
    entry: Mapping[str, Any] | IntegrationLogEntryDraft | None = None,
    *,
    payload: Any = None,
    **changes: Any,
) -> dict[str, Any]:
    """Return a DocType-shaped integration log payload."""

    draft = IntegrationLogEntryDraft.from_input(entry, **changes)
    if payload is not None:
        draft = replace(draft, payload=payload)
    return draft.to_doc()


__all__ = [
    "IntakeLineDraft",
    "IntakeSessionDraft",
    "IntegrationLogEntryDraft",
    "ProductProfileDraft",
    "SupplierSkuMappingDraft",
    "UnresolvedBarcodeDraft",
    "add_intake_line",
    "block_unsafe_intake_session",
    "build_integration_log_entry",
    "build_product_profile_doc",
    "build_supplier_sku_mapping_doc",
    "detect_unresolved_barcode",
    "intake_session_blockers",
    "open_intake_session",
    "post_safe_intake_session",
    "product_publishability_blockers",
    "validate_product_publishability",
]
