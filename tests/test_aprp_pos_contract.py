"""Core APRP POS and blackout-replay contract tests."""

import unittest
from pathlib import Path

from aprp.aprp import (
    FiscalReceiptReference,
    PosReceipt,
    PosReceiptLine,
    PosReplayBatch,
    PosReplayEntry,
    PosReplaySummary,
    build_pos_replay_summary,
)


class TestAprpPosContract(unittest.TestCase):
    """Verify POS capture, fiscalization, and replay stay explicit."""

    def test_pos_receipt_line_and_fiscal_reference_stay_explicit(self):
        """Ensure receipt lines and fiscal refs keep the capture data."""
        line = PosReceiptLine(
            barcode="APRP-ITEM-001",
            quantity=2,
            unit_price_eur=10.0,
            vat_rate=0.2,
            warehouse="Sofia - POS",
        )
        fiscal = FiscalReceiptReference(
            receipt_number="0001",
            device_name="Datecs-01",
            issued_at="2026-05-13T10:00:00+03:00",
            payment_method="cash",
            gross_total_eur=20.0,
        )

        self.assertEqual(20.0, line.line_total_eur())
        self.assertTrue(line.is_valid())
        self.assertEqual(
            "Datecs-01|0001|2026-05-13T10:00:00+03:00",
            fiscal.fiscal_key(),
        )
        self.assertTrue(fiscal.is_issued())

    def test_pos_receipt_and_replay_entry_keep_posting_state_explicit(self):
        """Ensure receipts and replay entries keep blackout state visible."""
        line = PosReceiptLine(
            barcode="APRP-ITEM-001",
            quantity=2,
            unit_price_eur=10.0,
            vat_rate=0.2,
            warehouse="Sofia - POS",
        )
        fiscal = FiscalReceiptReference(
            receipt_number="0001",
            device_name="Datecs-01",
            issued_at="2026-05-13T10:00:00+03:00",
            payment_method="cash",
            gross_total_eur=20.0,
        )
        receipt = PosReceipt(
            receipt_id="R-1",
            pos_id="POS-1",
            receipt_datetime="2026-05-13T10:00:00+03:00",
            payment_method="cash",
            fiscal_receipt=fiscal,
            declared_gross_eur=20.0,
            receipt_lines=(line,),
        )
        entry = PosReplayEntry(
            entry_id="ENTRY-1",
            source_name="datecs.csv",
            source_kind="datecs",
            receipt=receipt,
            queued_at="2026-05-13T07:00:00Z",
            replay_state="Posted",
            replayed_at="2026-05-13T07:05:00Z",
        )

        self.assertEqual(
            "R-1|POS-1|2026-05-13T10:00:00+03:00",
            receipt.receipt_key(),
        )
        self.assertEqual(20.0, receipt.gross_total_eur())
        self.assertEqual(2.0, receipt.quantity_total())
        self.assertEqual(1, receipt.line_count())
        self.assertTrue(receipt.fiscalized())
        self.assertEqual(0.0, receipt.gross_delta_eur())
        self.assertFalse(receipt.needs_review())
        self.assertTrue(receipt.is_replayable())
        self.assertTrue(entry.is_posted())
        self.assertFalse(entry.is_pending())
        self.assertFalse(entry.needs_review())

    def test_pos_replay_summary_rolls_up_blackout_state(self):
        """Ensure replay batches turn captured receipts into a summary."""
        receipt_line = PosReceiptLine(
            barcode="APRP-ITEM-001",
            quantity=2,
            unit_price_eur=10.0,
            vat_rate=0.2,
            warehouse="Sofia - POS",
        )
        fiscal = FiscalReceiptReference(
            receipt_number="0001",
            device_name="Datecs-01",
            issued_at="2026-05-13T10:00:00+03:00",
            payment_method="cash",
            gross_total_eur=20.0,
        )
        receipt_one = PosReceipt(
            receipt_id="R-1",
            pos_id="POS-1",
            receipt_datetime="2026-05-13T10:00:00+03:00",
            payment_method="cash",
            fiscal_receipt=fiscal,
            declared_gross_eur=20.0,
            receipt_lines=(receipt_line,),
        )
        receipt_two = PosReceipt(
            receipt_id="R-1",
            pos_id="POS-1",
            receipt_datetime="2026-05-13T10:00:00+03:00",
            payment_method="cash",
            declared_gross_eur=12.0,
            receipt_lines=(
                PosReceiptLine(
                    barcode="APRP-ITEM-002",
                    quantity=1,
                    unit_price_eur=10.0,
                    vat_rate=0.2,
                    warehouse="Sofia - POS",
                ),
            ),
        )
        entry_one = PosReplayEntry(
            entry_id="ENTRY-1",
            source_name="datecs.csv",
            source_kind="datecs",
            receipt=receipt_one,
            queued_at="2026-05-13T07:00:00Z",
            replay_state="Posted",
            replayed_at="2026-05-13T07:05:00Z",
        )
        entry_two = PosReplayEntry(
            entry_id="ENTRY-2",
            source_name="datecs.csv",
            source_kind="datecs",
            receipt=receipt_two,
            queued_at="2026-05-13T07:10:00Z",
            replay_state="Queued",
        )
        batch = PosReplayBatch(
            batch_id="BATCH-1",
            blackout_state="Closed",
            receipts=(receipt_one, receipt_two),
            replay_entries=(entry_one, entry_two),
        )

        summary = build_pos_replay_summary(batch)

        self.assertIsInstance(summary, PosReplaySummary)
        self.assertEqual(2, summary.receipt_count)
        self.assertEqual(2, summary.line_count)
        self.assertEqual(30.0, summary.gross_total_eur)
        self.assertEqual(1, summary.posted_count)
        self.assertEqual(1, summary.pending_count)
        self.assertEqual(1, summary.fiscalized_count)
        self.assertEqual(1, summary.duplicate_receipt_count)
        self.assertEqual(1, summary.mismatch_receipt_count)
        self.assertEqual("Closed", summary.blackout_state)
        self.assertTrue(summary.review_required)
        self.assertFalse(summary.is_clear())

    def test_pos_docs_cover_the_replay_contract(self):
        """Ensure the POS guide names the replay contract directly."""
        pos = Path("docs/pos.md").read_text(encoding="utf-8")

        for token in [
            "aprp.aprp.pos_contract",
            "Pos Receipt Line",
            "Fiscal Receipt Reference",
            "Pos Replay Entry",
            "Pos Replay Batch",
            "Pos Replay Summary",
            "Datecs",
            "blackout replay",
        ]:
            self.assertIn(token, pos)

    def test_contract_symbols_stay_explicit(self):
        """Ensure the exported POS symbols stay named directly."""
        self.assertEqual(PosReceiptLine.__name__, "PosReceiptLine")
        self.assertEqual(
            FiscalReceiptReference.__name__,
            "FiscalReceiptReference",
        )
        self.assertEqual(PosReceipt.__name__, "PosReceipt")
        self.assertEqual(PosReplayEntry.__name__, "PosReplayEntry")
        self.assertEqual(PosReplayBatch.__name__, "PosReplayBatch")
        self.assertEqual(PosReplaySummary.__name__, "PosReplaySummary")
        self.assertEqual(
            build_pos_replay_summary.__name__,
            "build_pos_replay_summary",
        )
