"""Core APRP POS, fiscalization, and blackout-replay contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PosReceiptLine:
    """Describe one receipt line captured from POS or Datecs output."""

    barcode: str
    quantity: float
    unit_price_eur: float
    vat_rate: float = 0.0
    warehouse: str = ""
    notes: str = ""

    def line_total_eur(self) -> float:
        """Return the rounded line total for the captured quantity."""

        return round(self.quantity * self.unit_price_eur, 2)

    def is_valid(self) -> bool:
        """Return whether the captured line is postable into ERP."""

        return (
            bool(self.barcode.strip())
            and self.quantity > 0
            and (self.unit_price_eur >= 0)
        )


@dataclass(frozen=True)
class FiscalReceiptReference:
    """Describe one fiscal receipt reference from a register or device."""

    receipt_number: str
    device_name: str
    issued_at: str
    payment_method: str
    gross_total_eur: float
    notes: str = ""

    def fiscal_key(self) -> str:
        """Return the stable fiscal reference key."""

        return "|".join(
            [
                self.device_name.strip(),
                self.receipt_number.strip(),
                self.issued_at.strip(),
            ]
        )

    def is_issued(self) -> bool:
        """Return whether the fiscal reference is populated."""

        return bool(self.receipt_number.strip()) and bool(
            self.device_name.strip()
        )


@dataclass(frozen=True)
class PosReceipt:
    """Describe one imported receipt and its ERP replay state."""

    receipt_id: str
    pos_id: str
    receipt_datetime: str
    payment_method: str
    capture_state: str = "Captured"
    replay_state: str = "Queued"
    currency: str = "BGN"
    customer_ref: str = ""
    operator_name: str = ""
    declared_gross_eur: float | None = None
    fiscal_receipt: FiscalReceiptReference | None = None
    receipt_lines: tuple[PosReceiptLine, ...] = ()
    notes: str = ""

    def receipt_key(self) -> str:
        """Return the idempotence key for one POS receipt."""

        return "|".join(
            [
                self.receipt_id.strip(),
                self.pos_id.strip(),
                self.receipt_datetime.strip(),
            ]
        )

    def gross_total_eur(self) -> float:
        """Return the rounded gross total from the receipt lines."""

        return round(
            sum(line.line_total_eur() for line in self.receipt_lines),
            2,
        )

    def quantity_total(self) -> float:
        """Return the total quantity captured on the receipt."""

        return round(sum(line.quantity for line in self.receipt_lines), 2)

    def line_count(self) -> int:
        """Return the number of receipt lines."""

        return len(self.receipt_lines)

    def fiscalized(self) -> bool:
        """Return whether the receipt already has a fiscal reference."""

        return (
            self.fiscal_receipt is not None and self.fiscal_receipt.is_issued()
        )

    def gross_delta_eur(self) -> float:
        """Return the delta between declared and computed gross totals."""

        if self.declared_gross_eur is None:
            return 0.0
        return round(self.declared_gross_eur - self.gross_total_eur(), 2)

    def needs_review(self) -> bool:
        """Return whether the receipt needs operator review."""

        capture_state = self.capture_state.strip().lower()
        replay_state = self.replay_state.strip().lower()
        if capture_state in {"failed", "rejected"}:
            return True
        if replay_state in {"failed", "requires_review"}:
            return True
        if any(not line.is_valid() for line in self.receipt_lines):
            return True
        return abs(self.gross_delta_eur()) > 0.01

    def is_replayable(self) -> bool:
        """Return whether the receipt can still move through replay."""

        capture_state = self.capture_state.strip().lower()
        return capture_state in {"captured", "queued", "replay_required"}


@dataclass(frozen=True)
class PosReplayEntry:
    """Describe one queued blackout-replay entry."""

    entry_id: str
    source_name: str
    source_kind: str
    receipt: PosReceipt
    queued_at: str
    replay_state: str = "Queued"
    replayed_at: str = ""
    note: str = ""

    def receipt_key(self) -> str:
        """Return the receipt key for this replay entry."""

        return self.receipt.receipt_key()

    def is_posted(self) -> bool:
        """Return whether the entry has already been posted to ERP."""

        return self.replay_state.strip().lower() == "posted"

    def is_pending(self) -> bool:
        """Return whether the entry still waits for replay."""

        return self.replay_state.strip().lower() == "queued"

    def needs_review(self) -> bool:
        """Return whether the replay entry needs operator review."""

        replay_state = self.replay_state.strip().lower()
        return replay_state in {"failed", "requires_review"} or (
            self.receipt.needs_review()
        )


@dataclass(frozen=True)
class PosReplayBatch:
    """Describe one replay batch grouped for blackout recovery."""

    batch_id: str
    blackout_state: str = "Open"
    receipts: tuple[PosReceipt, ...] = ()
    replay_entries: tuple[PosReplayEntry, ...] = ()
    notes: str = ""

    def receipt_count(self) -> int:
        """Return the number of receipts in the batch."""

        return len(self.receipts)

    def line_count(self) -> int:
        """Return the number of receipt lines in the batch."""

        return sum(receipt.line_count() for receipt in self.receipts)

    def gross_total_eur(self) -> float:
        """Return the rounded gross total for the batch."""

        return round(
            sum(receipt.gross_total_eur() for receipt in self.receipts),
            2,
        )

    def posted_count(self) -> int:
        """Return the number of replay entries already posted."""

        return sum(1 for entry in self.replay_entries if entry.is_posted())

    def pending_count(self) -> int:
        """Return the number of replay entries still queued."""

        return sum(1 for entry in self.replay_entries if entry.is_pending())

    def fiscalized_count(self) -> int:
        """Return the number of receipts that already carry fiscal refs."""

        return sum(1 for receipt in self.receipts if receipt.fiscalized())

    def duplicate_receipt_count(self) -> int:
        """Return the number of duplicate receipt keys in the batch."""

        seen: set[str] = set()
        duplicates = 0
        for receipt in self.receipts:
            key = receipt.receipt_key()
            if key in seen:
                duplicates += 1
            else:
                seen.add(key)
        return duplicates

    def mismatch_receipt_count(self) -> int:
        """Return the number of receipts that need review."""

        return sum(1 for receipt in self.receipts if receipt.needs_review())

    def review_required(self) -> bool:
        """Return whether the batch needs operator review."""

        return (
            self.blackout_state.strip().lower() != "closed"
            or self.duplicate_receipt_count() > 0
            or self.mismatch_receipt_count() > 0
            or any(entry.needs_review() for entry in self.replay_entries)
        )


@dataclass(frozen=True)
class PosReplaySummary:
    """Describe one operator-facing blackout replay summary."""

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

    def is_clear(self) -> bool:
        """Return whether the batch is clear for final posting."""

        return not self.review_required and self.pending_count == 0


def build_pos_replay_summary(batch: PosReplayBatch) -> PosReplaySummary:
    """Build a blackout replay summary from one POS batch."""

    return PosReplaySummary(
        batch_id=batch.batch_id,
        receipt_count=batch.receipt_count(),
        line_count=batch.line_count(),
        gross_total_eur=batch.gross_total_eur(),
        posted_count=batch.posted_count(),
        pending_count=batch.pending_count(),
        fiscalized_count=batch.fiscalized_count(),
        duplicate_receipt_count=batch.duplicate_receipt_count(),
        mismatch_receipt_count=batch.mismatch_receipt_count(),
        blackout_state=batch.blackout_state,
        review_required=batch.review_required(),
    )


__all__ = [
    "FiscalReceiptReference",
    "PosReceipt",
    "PosReceiptLine",
    "PosReplayBatch",
    "PosReplayEntry",
    "PosReplaySummary",
    "build_pos_replay_summary",
]
