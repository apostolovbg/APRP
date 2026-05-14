"""APRP POS service helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass, replace
from typing import Any, Protocol, runtime_checkable

from .pos_contract import (
    FiscalReceiptReference,
    PosReceipt,
    PosReceiptLine,
    PosReplayBatch,
    PosReplayEntry,
    PosReplaySummary,
    build_pos_replay_summary,
)


def _clean_text(value: Any) -> str:
    """Return a stripped text representation."""

    if value is None:
        return ""
    return str(value).strip()


def _coerce_float(value: Any) -> float:
    """Return a float representation for POS quantities and totals."""

    if value in {None, ""}:
        return 0.0
    return float(value)


def _coerce_bool(value: Any) -> bool:
    """Return a stable boolean representation for POS inputs."""

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _mapping_from_input(value: Any) -> dict[str, Any]:
    """Return a mapping view for dict-like or dataclass inputs."""

    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"unsupported POS input: {type(value)!r}")


def _split_receipt_datetime(receipt_datetime: str) -> tuple[str, str]:
    """Split a receipt timestamp into date and time parts."""

    text = _clean_text(receipt_datetime)
    if not text:
        return "", ""
    if "T" in text:
        date_part, time_part = text.split("T", 1)
        return date_part, time_part
    if " " in text:
        date_part, time_part = text.split(" ", 1)
        return date_part, time_part
    return text[:10], ""


def _normalize_payment_method(value: Any) -> str:
    """Return a canonical payment-method label."""

    return _clean_text(value) or "cash"


def _normalize_pos_receipt_line(
    value: Mapping[str, Any] | PosReceiptLine,
) -> PosReceiptLine:
    """Return a normalized POS receipt line."""

    line_data = _mapping_from_input(value)
    return PosReceiptLine(
        barcode=_clean_text(line_data.get("barcode")),
        quantity=_coerce_float(line_data.get("quantity")),
        unit_price_eur=_coerce_float(line_data.get("unit_price_eur")),
        vat_rate=_coerce_float(line_data.get("vat_rate")),
        warehouse=_clean_text(line_data.get("warehouse")),
        notes=_clean_text(line_data.get("notes")),
    )


def _normalize_fiscal_reference(
    value: Mapping[str, Any] | FiscalReceiptReference | None,
) -> FiscalReceiptReference | None:
    """Return a normalized fiscal receipt reference."""

    if value is None:
        return None
    reference_data = _mapping_from_input(value)
    receipt_number = _clean_text(reference_data.get("receipt_number"))
    device_name = _clean_text(reference_data.get("device_name"))
    issued_at = _clean_text(reference_data.get("issued_at"))
    payment_method = _normalize_payment_method(
        reference_data.get("payment_method")
    )
    gross_total_eur = _coerce_float(reference_data.get("gross_total_eur"))
    notes = _clean_text(reference_data.get("notes"))
    if not receipt_number or not device_name or not issued_at:
        raise ValueError("fiscal receipt reference requires receipt fields")
    return FiscalReceiptReference(
        receipt_number=receipt_number,
        device_name=device_name,
        issued_at=issued_at,
        payment_method=payment_method,
        gross_total_eur=gross_total_eur,
        notes=notes,
    )


def _normalize_pos_receipt(
    value: Mapping[str, Any] | PosReceipt | "PosReceiptDraft",
    *,
    receipt_lines: Iterable[Mapping[str, Any] | PosReceiptLine] = (),
    fiscal_capture: Mapping[str, Any] | FiscalReceiptReference | None = None,
    source_system: str = "",
) -> PosReceipt:
    """Return a normalized POS receipt contract."""

    receipt_data = _mapping_from_input(value)
    lines_input = receipt_data.get("receipt_lines", receipt_lines)
    normalized_lines = tuple(
        _normalize_pos_receipt_line(line) for line in lines_input
    )
    normalized_fiscal = _normalize_fiscal_reference(
        receipt_data.get(
            "fiscal_receipt",
            receipt_data.get("fiscal_capture", fiscal_capture),
        )
    )
    receipt_id = _clean_text(receipt_data.get("receipt_id"))
    if not receipt_id:
        receipt_id = _clean_text(receipt_data.get("receipt_number"))
    pos_id = _clean_text(receipt_data.get("pos_id"))
    if not pos_id:
        pos_id = _clean_text(source_system)
    receipt_datetime = _clean_text(receipt_data.get("receipt_datetime"))
    payment_method = _normalize_payment_method(
        receipt_data.get("payment_method")
    )
    if not receipt_id:
        raise ValueError("receipt_id is required")
    if not pos_id:
        raise ValueError("pos_id is required")
    if not receipt_datetime:
        raise ValueError("receipt_datetime is required")
    if not normalized_lines:
        raise ValueError("receipt_lines are required")
    capture_state = (
        _clean_text(receipt_data.get("capture_state")) or "Captured"
    )
    replay_state = _clean_text(receipt_data.get("replay_state")) or "Queued"
    return PosReceipt(
        receipt_id=receipt_id,
        pos_id=pos_id,
        receipt_datetime=receipt_datetime,
        payment_method=payment_method,
        capture_state=capture_state,
        replay_state=replay_state,
        currency=_clean_text(receipt_data.get("currency")) or "BGN",
        customer_ref=_clean_text(receipt_data.get("customer_ref")),
        operator_name=_clean_text(receipt_data.get("operator_name")),
        declared_gross_eur=(
            None
            if receipt_data.get("declared_gross_eur") in {None, ""}
            else _coerce_float(receipt_data.get("declared_gross_eur"))
        ),
        fiscal_receipt=normalized_fiscal,
        receipt_lines=normalized_lines,
        notes=_clean_text(receipt_data.get("notes")),
    )


def _receipt_validation_blockers(receipt: PosReceipt) -> tuple[str, ...]:
    """Return the structural blockers for one receipt."""

    blockers: list[str] = []
    if not receipt.receipt_id.strip():
        blockers.append("receipt_id")
    if not receipt.pos_id.strip():
        blockers.append("pos_id")
    if not receipt.receipt_datetime.strip():
        blockers.append("receipt_datetime")
    if not receipt.receipt_lines:
        blockers.append("receipt_lines")
    for line in receipt.receipt_lines:
        if not line.is_valid():
            blockers.append(f"{line.barcode or 'line'}:invalid")
    return tuple(blockers)


def _derive_location(receipt: PosReceipt) -> str:
    """Return the best available POS location for one receipt."""

    for line in receipt.receipt_lines:
        if line.warehouse.strip():
            return line.warehouse.strip()
    return receipt.pos_id.strip()


def _derive_receipt_status(
    receipt: PosReceipt,
    blockers: tuple[str, ...],
) -> str:
    """Return the doctype status for one receipt."""

    if blockers:
        return "Failed"
    if receipt.needs_review():
        return "Imported"
    if (
        receipt.fiscalized()
        and receipt.replay_state.strip().lower() == "posted"
    ):
        return "Posted"
    return "Imported"


def _derive_entry_state(
    receipt: PosReceipt,
    blockers: tuple[str, ...],
) -> tuple[str, str]:
    """Return the replay and operator states for one receipt."""

    if blockers:
        return "Failed", "Blocked"
    if receipt.needs_review():
        return "Requires Review", "Review Required"
    if receipt.replay_state.strip().lower() == "posted":
        return "Posted", "Cleared"
    if receipt.replay_state.strip().lower() == "skipped":
        return "Skipped", "Skipped"
    return "Queued", "Queued"


def _derive_batch_status(
    receipts: tuple["PosReceiptDraft", ...],
    replay_entries: tuple["PosReplayEntryDraft", ...],
    blackout_state: str,
    explicit_status: str,
) -> str:
    """Return the most appropriate batch status."""

    if explicit_status:
        return explicit_status
    if not receipts:
        return "Draft"
    if any(entry.replay_state == "Failed" for entry in replay_entries):
        return "Failed"
    if any(
        entry.replay_state == "Requires Review" for entry in replay_entries
    ):
        return "Ready"
    if blackout_state.strip().lower() == "closed" and all(
        entry.replay_state == "Posted" for entry in replay_entries
    ):
        return "Posted"
    return "In Progress"


def _count_duplicates(items: Iterable[str]) -> int:
    """Return the number of duplicate entries in one sequence."""

    seen: set[str] = set()
    duplicates = 0
    for item in items:
        if item in seen:
            duplicates += 1
        else:
            seen.add(item)
    return duplicates


@dataclass(frozen=True)
class FiscalReceiptCaptureDraft:
    """Describe one captured fiscal receipt reference."""

    receipt_number: str
    device_name: str
    issued_at: str
    payment_method: str
    gross_total_eur: float
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the fiscal capture payload as a plain dictionary."""

        return asdict(self)

    def to_contract(self) -> FiscalReceiptReference:
        """Return the canonical fiscal receipt reference contract."""

        return FiscalReceiptReference(
            receipt_number=self.receipt_number,
            device_name=self.device_name,
            issued_at=self.issued_at,
            payment_method=self.payment_method,
            gross_total_eur=self.gross_total_eur,
            notes=self.notes,
        )


@dataclass(frozen=True)
class PosReceiptLineDraft:
    """Describe one mapped POS receipt line."""

    barcode: str
    quantity: float
    unit_price_eur: float
    vat_rate: float = 0.0
    warehouse: str = ""
    notes: str = ""

    def to_doc(self) -> dict[str, Any]:
        """Return the receipt line as a plain dictionary."""

        return asdict(self)

    def to_contract(self) -> PosReceiptLine:
        """Return the canonical POS receipt line contract."""

        return PosReceiptLine(
            barcode=self.barcode,
            quantity=self.quantity,
            unit_price_eur=self.unit_price_eur,
            vat_rate=self.vat_rate,
            warehouse=self.warehouse,
            notes=self.notes,
        )


@dataclass(frozen=True)
class PosReceiptDraft:
    """Describe one imported POS receipt draft."""

    receipt_number: str
    location: str
    receipt_datetime: str
    cashier: str
    customer: str
    payment_method: str
    grand_total: float
    declared_gross_eur: float | None = None
    currency: str = "BGN"
    source_system: str = ""
    status: str = "Draft"
    capture_state: str = "Captured"
    replay_state: str = "Queued"
    fiscal_capture: FiscalReceiptCaptureDraft | None = None
    receipt_lines: tuple[PosReceiptLineDraft, ...] = ()
    review_required: bool = False
    validation_blockers: tuple[str, ...] = ()
    notes: str = ""

    def posting_date(self) -> str:
        """Return the posting date derived from the receipt timestamp."""

        return _split_receipt_datetime(self.receipt_datetime)[0]

    def line_count(self) -> int:
        """Return the number of receipt lines in the draft."""

        return len(self.receipt_lines)

    def needs_review(self) -> bool:
        """Return whether the draft should be reviewed before posting."""

        return self.review_required or bool(self.validation_blockers)

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped receipt payload."""

        fiscal_number = ""
        if self.fiscal_capture is not None:
            fiscal_number = self.fiscal_capture.receipt_number
        return {
            "receipt_number": self.receipt_number,
            "location": self.location,
            "posting_date": self.posting_date(),
            "cashier": self.cashier,
            "customer": self.customer,
            "grand_total": self.grand_total,
            "currency": self.currency,
            "fiscal_number": fiscal_number,
            "source_system": self.source_system,
            "status": self.status,
            "notes": self.notes,
        }

    def to_contract(self) -> PosReceipt:
        """Return the canonical POS receipt contract."""

        fiscal_reference = None
        if self.fiscal_capture is not None:
            fiscal_reference = self.fiscal_capture.to_contract()
        return PosReceipt(
            receipt_id=self.receipt_number,
            pos_id=self.source_system or self.location,
            receipt_datetime=self.receipt_datetime,
            payment_method=self.payment_method,
            capture_state=self.capture_state,
            replay_state=self.replay_state,
            currency=self.currency,
            customer_ref=self.customer,
            operator_name=self.cashier,
            declared_gross_eur=(
                self.declared_gross_eur
                if self.declared_gross_eur is not None
                else self.grand_total
            ),
            fiscal_receipt=fiscal_reference,
            receipt_lines=tuple(
                line.to_contract() for line in self.receipt_lines
            ),
            notes=self.notes,
        )


@dataclass(frozen=True)
class PosReplayEntryDraft:
    """Describe one blackout replay entry draft."""

    entry_id: str
    source_name: str
    source_kind: str
    receipt_number: str
    queued_at: str
    replay_state: str = "Queued"
    replayed_at: str = ""
    operator_state: str = "Queued"
    note: str = ""
    review_required: bool = False
    validation_blockers: tuple[str, ...] = ()

    def to_doc(self) -> dict[str, Any]:
        """Return the replay entry as a plain dictionary."""

        return asdict(self)

    def to_contract(self, receipt: PosReceipt) -> PosReplayEntry:
        """Return the canonical POS replay entry contract."""

        return PosReplayEntry(
            entry_id=self.entry_id,
            source_name=self.source_name,
            source_kind=self.source_kind,
            receipt=receipt,
            queued_at=self.queued_at,
            replay_state=self.replay_state,
            replayed_at=self.replayed_at,
            note=self.note,
        )


@dataclass(frozen=True)
class PosReplayBatchDraft:
    """Describe one blackout replay batch draft."""

    batch_id: str
    location: str
    blackout_state: str = "Open"
    status: str = "Draft"
    received_on: str = ""
    receipt_count: int = 0
    notes: str = ""
    receipts: tuple[PosReceiptDraft, ...] = ()
    replay_entries: tuple[PosReplayEntryDraft, ...] = ()
    review_required: bool = False
    operator_state: str = "Queued"
    validation_blockers: tuple[str, ...] = ()

    def is_clear(self) -> bool:
        """Return whether the batch is clear for posting."""

        return (
            not self.review_required
            and not self.validation_blockers
            and self.status in {"Posted", "Ready"}
        )

    def to_doc(self) -> dict[str, Any]:
        """Return the DocType-shaped batch payload."""

        return {
            "batch_id": self.batch_id,
            "location": self.location,
            "status": self.status,
            "received_on": self.received_on,
            "receipt_count": self.receipt_count,
            "notes": self.notes,
            "receipts": [receipt.to_doc() for receipt in self.receipts],
        }

    def to_contract(self) -> PosReplayBatch:
        """Return the canonical POS replay batch contract."""

        receipt_map = {
            receipt.receipt_number: receipt.to_contract()
            for receipt in self.receipts
        }
        replay_entries = tuple(
            entry.to_contract(receipt_map[entry.receipt_number])
            for entry in self.replay_entries
            if entry.receipt_number in receipt_map
        )
        return PosReplayBatch(
            batch_id=self.batch_id,
            blackout_state=self.blackout_state,
            receipts=tuple(receipt.to_contract() for receipt in self.receipts),
            replay_entries=replay_entries,
            notes=self.notes,
        )


@dataclass(frozen=True)
class PosReplaySummaryDraft:
    """Describe one operator-facing POS replay summary draft."""

    batch_id: str
    receipt_count: int
    line_count: int
    gross_total_eur: float
    posted_count: int
    pending_count: int
    fiscalized_count: int
    duplicate_receipt_count: int
    mismatch_receipt_count: int
    blackout_state: str
    review_required: bool
    operator_state: str

    def is_clear(self) -> bool:
        """Return whether the replay summary is clear for final posting."""

        return (
            not self.review_required
            and self.pending_count == 0
            and self.operator_state == "Cleared"
        )

    def to_doc(self) -> dict[str, Any]:
        """Return the summary as a plain dictionary."""

        return asdict(self)

    def to_contract(self, batch: PosReplayBatch) -> PosReplaySummary:
        """Return the canonical POS replay summary contract."""

        return build_pos_replay_summary(batch)


@runtime_checkable
class PosAdapter(Protocol):
    """Describe the POS adapter contract."""

    adapter_name: str
    source_kind: str
    location: str

    def validate_receipt(
        self, receipt: Mapping[str, Any] | PosReceipt
    ) -> tuple[str, ...]:
        """Return the structural receipt blockers."""

    def build_pos_receipt_doc(
        self,
        receipt: Mapping[str, Any] | PosReceipt,
    ) -> PosReceiptDraft:
        """Return one normalized POS receipt draft."""

    def build_pos_replay_entry(
        self,
        receipt: Mapping[str, Any] | PosReceipt,
        *,
        entry_id: str,
        queued_at: str = "",
        replayed_at: str = "",
        source_name: str = "",
        note: str = "",
    ) -> PosReplayEntryDraft:
        """Return one replay entry draft for a receipt."""

    def build_pos_replay_batch_doc(
        self,
        *,
        batch_id: str,
        receipts: Iterable[Mapping[str, Any] | PosReceipt],
        replay_entries: Iterable[PosReplayEntryDraft] = (),
        blackout_state: str = "Open",
        status: str = "",
        received_on: str = "",
        notes: str = "",
    ) -> PosReplayBatchDraft:
        """Return one replay batch draft."""

    def build_pos_replay_summary_doc(
        self,
        batch: PosReplayBatchDraft,
    ) -> PosReplaySummaryDraft:
        """Return one replay summary draft."""


@dataclass(frozen=True)
class _PosAdapterBase:
    """Shared adapter behavior for POS capture and replay helpers."""

    location: str
    source_kind: str = "datecs"
    adapter_name: str = "APRP POS"

    def validate_receipt(
        self, receipt: Mapping[str, Any] | PosReceipt
    ) -> tuple[str, ...]:
        """Return the structural receipt blockers."""

        normalized = _normalize_pos_receipt(
            receipt, source_system=self.source_kind
        )
        return _receipt_validation_blockers(normalized)

    def build_pos_receipt_doc(
        self,
        receipt: Mapping[str, Any] | PosReceipt,
    ) -> PosReceiptDraft:
        """Return one normalized POS receipt draft."""

        normalized = _normalize_pos_receipt(
            receipt,
            source_system=self.source_kind,
        )
        blockers = _receipt_validation_blockers(normalized)
        receipt_lines = tuple(
            PosReceiptLineDraft(
                barcode=line.barcode,
                quantity=line.quantity,
                unit_price_eur=line.unit_price_eur,
                vat_rate=line.vat_rate,
                warehouse=line.warehouse,
                notes=line.notes,
            )
            for line in normalized.receipt_lines
        )
        fiscal_capture = None
        if normalized.fiscal_receipt is not None:
            fiscal_capture = FiscalReceiptCaptureDraft(
                receipt_number=normalized.fiscal_receipt.receipt_number,
                device_name=normalized.fiscal_receipt.device_name,
                issued_at=normalized.fiscal_receipt.issued_at,
                payment_method=normalized.fiscal_receipt.payment_method,
                gross_total_eur=normalized.fiscal_receipt.gross_total_eur,
                notes=normalized.fiscal_receipt.notes,
            )
        status = _derive_receipt_status(normalized, blockers)
        return PosReceiptDraft(
            receipt_number=normalized.receipt_id,
            location=_derive_location(normalized),
            receipt_datetime=normalized.receipt_datetime,
            cashier=normalized.operator_name,
            customer=normalized.customer_ref,
            payment_method=normalized.payment_method,
            grand_total=normalized.gross_total_eur(),
            declared_gross_eur=normalized.declared_gross_eur,
            currency=normalized.currency,
            source_system=normalized.pos_id,
            status=status,
            capture_state=normalized.capture_state,
            replay_state=normalized.replay_state,
            fiscal_capture=fiscal_capture,
            receipt_lines=receipt_lines,
            review_required=normalized.needs_review(),
            validation_blockers=blockers,
            notes=normalized.notes,
        )

    def build_pos_replay_entry(
        self,
        receipt: Mapping[str, Any] | PosReceipt,
        *,
        entry_id: str,
        queued_at: str = "",
        replayed_at: str = "",
        source_name: str = "",
        note: str = "",
    ) -> PosReplayEntryDraft:
        """Return one replay entry draft for a receipt."""

        normalized = _normalize_pos_receipt(
            receipt,
            source_system=self.source_kind,
        )
        blockers = _receipt_validation_blockers(normalized)
        replay_state, operator_state = _derive_entry_state(
            normalized,
            blockers,
        )
        replay_note = _clean_text(note)
        if blockers:
            replay_note = ", ".join(blockers)
        elif normalized.needs_review() and not replay_note:
            replay_note = "Receipt requires review"
        return PosReplayEntryDraft(
            entry_id=_clean_text(entry_id),
            source_name=_clean_text(source_name) or self.adapter_name,
            source_kind=self.source_kind,
            receipt_number=normalized.receipt_id,
            queued_at=_clean_text(queued_at),
            replay_state=replay_state,
            replayed_at=_clean_text(replayed_at),
            operator_state=operator_state,
            note=replay_note,
            review_required=replay_state == "Requires Review",
            validation_blockers=blockers,
        )

    def build_pos_replay_batch_doc(
        self,
        *,
        batch_id: str,
        receipts: Iterable[Mapping[str, Any] | PosReceipt],
        replay_entries: Iterable[PosReplayEntryDraft] = (),
        blackout_state: str = "Open",
        status: str = "",
        received_on: str = "",
        notes: str = "",
    ) -> PosReplayBatchDraft:
        """Return one replay batch draft."""

        normalized_receipts = tuple(
            _normalize_pos_receipt(
                receipt,
                source_system=self.source_kind,
            )
            for receipt in receipts
        )
        receipt_drafts = tuple(
            self.build_pos_receipt_doc(receipt)
            for receipt in normalized_receipts
        )
        replay_entry_drafts = tuple(replay_entries)
        if not replay_entry_drafts:
            replay_entry_drafts = tuple(
                self.build_pos_replay_entry(
                    receipt,
                    entry_id=f"{_clean_text(batch_id)}-{index + 1}",
                    queued_at=received_on,
                )
                for index, receipt in enumerate(normalized_receipts)
            )
        validation_blockers = tuple(
            blocker
            for receipt in receipt_drafts
            for blocker in receipt.validation_blockers
        )
        derived_status = _derive_batch_status(
            receipt_drafts,
            replay_entry_drafts,
            blackout_state,
            _clean_text(status),
        )
        operator_state = "Queued"
        if validation_blockers:
            operator_state = "Blocked"
        elif any(
            entry.replay_state == "Requires Review"
            for entry in replay_entry_drafts
        ):
            operator_state = "Review Required"
        elif derived_status == "Posted":
            operator_state = "Cleared"
        elif derived_status == "Ready":
            operator_state = "Review Required"
        elif derived_status == "In Progress":
            operator_state = "In Progress"
        if not batch_id:
            raise ValueError("batch_id is required")
        if not receipt_drafts:
            derived_status = "Draft"
        if not received_on and receipt_drafts:
            received_on = receipt_drafts[0].receipt_datetime
        if not _clean_text(self.location):
            raise ValueError("location is required")
        return PosReplayBatchDraft(
            batch_id=_clean_text(batch_id),
            location=self.location,
            blackout_state=_clean_text(blackout_state) or "Open",
            status=derived_status,
            received_on=_clean_text(received_on),
            receipt_count=len(receipt_drafts),
            notes=_clean_text(notes),
            receipts=receipt_drafts,
            replay_entries=replay_entry_drafts,
            review_required=bool(validation_blockers)
            or any(
                entry.replay_state == "Requires Review"
                for entry in replay_entry_drafts
            ),
            operator_state=operator_state,
            validation_blockers=validation_blockers,
        )

    def build_pos_replay_summary_doc(
        self,
        batch: PosReplayBatchDraft,
    ) -> PosReplaySummaryDraft:
        """Return one replay summary draft."""

        contract_summary = build_pos_replay_summary(batch.to_contract())
        operator_state = (
            "Cleared" if contract_summary.is_clear() else "Review Required"
        )
        if batch.validation_blockers:
            operator_state = "Blocked"
        return PosReplaySummaryDraft(
            batch_id=contract_summary.batch_id,
            receipt_count=contract_summary.receipt_count,
            line_count=contract_summary.line_count,
            gross_total_eur=contract_summary.gross_total_eur,
            posted_count=contract_summary.posted_count,
            pending_count=contract_summary.pending_count,
            fiscalized_count=contract_summary.fiscalized_count,
            duplicate_receipt_count=contract_summary.duplicate_receipt_count,
            mismatch_receipt_count=contract_summary.mismatch_receipt_count,
            blackout_state=contract_summary.blackout_state,
            review_required=contract_summary.review_required,
            operator_state=operator_state,
        )


@dataclass(frozen=True)
class PosSimulatorAdapter(_PosAdapterBase):
    """Describe the local POS simulator adapter shell."""

    adapter_name: str = "Simulator"

    def sample_receipts(self) -> tuple[PosReceipt, ...]:
        """Return sample receipts for proof and smoke tests."""

        return (
            PosReceipt(
                receipt_id="R-2026-0001",
                pos_id="POS-1",
                receipt_datetime="2026-05-13T10:00:00+03:00",
                payment_method="cash",
                capture_state="Captured",
                replay_state="Queued",
                currency="BGN",
                customer_ref="WEB-2026-0001",
                operator_name="ops",
                declared_gross_eur=20.0,
                fiscal_receipt=FiscalReceiptReference(
                    receipt_number="0001",
                    device_name="Datecs-01",
                    issued_at="2026-05-13T10:01:00+03:00",
                    payment_method="cash",
                    gross_total_eur=20.0,
                ),
                receipt_lines=(
                    PosReceiptLine(
                        barcode="APRP-ITEM-001",
                        quantity=2,
                        unit_price_eur=10.0,
                        vat_rate=0.2,
                        warehouse="Sofia - POS",
                    ),
                ),
            ),
            PosReceipt(
                receipt_id="R-2026-0002",
                pos_id="POS-1",
                receipt_datetime="2026-05-13T10:15:00+03:00",
                payment_method="cash",
                capture_state="Captured",
                replay_state="Queued",
                currency="BGN",
                customer_ref="WEB-2026-0002",
                operator_name="ops",
                declared_gross_eur=12.0,
                receipt_lines=(
                    PosReceiptLine(
                        barcode="APRP-ITEM-002",
                        quantity=1,
                        unit_price_eur=11.0,
                        vat_rate=0.2,
                        warehouse="Sofia - POS",
                    ),
                ),
            ),
        )


def receipt_validation_blockers(
    receipt: Mapping[str, Any] | PosReceipt | PosReceiptDraft,
) -> tuple[str, ...]:
    """Return the structural receipt blockers for one receipt."""

    normalized = _normalize_pos_receipt(receipt)
    return _receipt_validation_blockers(normalized)


def validate_pos_receipt(
    receipt: Mapping[str, Any] | PosReceipt | PosReceiptDraft,
) -> bool:
    """Return whether one receipt is structurally valid."""

    return not receipt_validation_blockers(receipt)


def build_pos_receipt_doc(
    receipt: Mapping[str, Any] | PosReceipt | PosReceiptDraft,
    *,
    location: str = "",
    source_system: str = "",
    status: str = "",
    notes: str = "",
) -> PosReceiptDraft:
    """Build one normalized POS receipt draft."""

    adapter = PosSimulatorAdapter(location=_clean_text(location) or "POS")
    normalized = _normalize_pos_receipt(
        receipt,
        source_system=_clean_text(source_system) or adapter.source_kind,
    )
    if location:
        adapter = PosSimulatorAdapter(
            location=_clean_text(location),
            source_kind=adapter.source_kind,
        )
    if not status:
        status = _derive_receipt_status(
            normalized,
            _receipt_validation_blockers(normalized),
        )
    draft = adapter.build_pos_receipt_doc(normalized)
    if location:
        draft = replace(draft, location=_clean_text(location))
    if notes:
        draft = replace(draft, notes=_clean_text(notes))
    if status:
        draft = replace(draft, status=_clean_text(status))
    return draft


def build_pos_replay_entry(
    receipt: Mapping[str, Any] | PosReceipt | PosReceiptDraft,
    *,
    entry_id: str,
    location: str = "",
    source_name: str = "",
    source_kind: str = "datecs",
    queued_at: str = "",
    replayed_at: str = "",
    note: str = "",
) -> PosReplayEntryDraft:
    """Build one normalized blackout replay entry draft."""

    adapter = PosSimulatorAdapter(
        location=_clean_text(location) or "POS",
        source_kind=_clean_text(source_kind) or "datecs",
    )
    normalized = _normalize_pos_receipt(
        receipt, source_system=adapter.source_kind
    )
    return adapter.build_pos_replay_entry(
        normalized,
        entry_id=entry_id,
        queued_at=queued_at,
        replayed_at=replayed_at,
        source_name=source_name,
        note=note,
    )


def build_pos_replay_batch_doc(
    *,
    batch_id: str,
    receipts: Iterable[Mapping[str, Any] | PosReceipt | PosReceiptDraft],
    location: str = "",
    source_kind: str = "datecs",
    blackout_state: str = "Open",
    status: str = "",
    received_on: str = "",
    notes: str = "",
    replay_entries: Iterable[PosReplayEntryDraft] = (),
) -> PosReplayBatchDraft:
    """Build one blackout replay batch draft."""

    location_value = _clean_text(location)
    normalized_receipts = tuple(
        _normalize_pos_receipt(
            receipt,
            source_system=_clean_text(source_kind) or "datecs",
        )
        for receipt in receipts
    )
    if not location_value and normalized_receipts:
        location_value = _derive_location(normalized_receipts[0])
    adapter = PosSimulatorAdapter(
        location=location_value or "POS",
        source_kind=_clean_text(source_kind) or "datecs",
    )
    return adapter.build_pos_replay_batch_doc(
        batch_id=batch_id,
        receipts=normalized_receipts,
        replay_entries=tuple(replay_entries),
        blackout_state=blackout_state,
        status=status,
        received_on=received_on,
        notes=notes,
    )


def build_pos_replay_summary_doc(
    batch: PosReplayBatchDraft,
) -> PosReplaySummaryDraft:
    """Build one operator-facing blackout replay summary draft."""

    adapter = PosSimulatorAdapter(
        location=batch.location,
        source_kind="datecs",
    )
    return adapter.build_pos_replay_summary_doc(batch)


__all__ = [
    "FiscalReceiptCaptureDraft",
    "PosAdapter",
    "PosReceiptDraft",
    "PosReceiptLineDraft",
    "PosReplayBatchDraft",
    "PosReplayEntryDraft",
    "PosReplaySummaryDraft",
    "PosSimulatorAdapter",
    "build_pos_receipt_doc",
    "build_pos_replay_batch_doc",
    "build_pos_replay_entry",
    "build_pos_replay_summary_doc",
    "receipt_validation_blockers",
    "validate_pos_receipt",
]
