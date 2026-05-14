"""POS service helper tests for APRP."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import aprp.aprp as package
from aprp.aprp import (
    FiscalReceiptCaptureDraft,
    PosAdapter,
    PosReceiptDraft,
    PosReceiptLineDraft,
    PosReplayBatchDraft,
    PosReplayEntryDraft,
    PosReplaySummaryDraft,
    PosSimulatorAdapter,
    build_pos_receipt_doc,
    build_pos_replay_batch_doc,
    build_pos_replay_entry,
    build_pos_replay_summary_doc,
    receipt_validation_blockers,
    validate_pos_receipt,
)


class TestAprpPosServices(unittest.TestCase):
    """Verify the POS service layer stays explicit."""

    def test_package_exports_pos_service_helpers(self):
        """Ensure the package exposes the POS service layer."""

        module = importlib.import_module("aprp.aprp.pos_services")
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")
        docs = Path("docs/pos.md").read_text(encoding="utf-8")

        self.assertIn("APRP", module.__doc__ or "")
        self.assertIn("aprp.aprp.pos_services", readme)
        self.assertIn("aprp.aprp.pos_services", spec)
        self.assertIn("aprp.aprp.pos_services", docs)
        self.assertIs(package.PosAdapter, PosAdapter)
        self.assertIs(
            package.FiscalReceiptCaptureDraft,
            FiscalReceiptCaptureDraft,
        )
        self.assertIs(package.PosReceiptDraft, PosReceiptDraft)
        self.assertIs(package.PosReceiptLineDraft, PosReceiptLineDraft)
        self.assertIs(package.PosReplayBatchDraft, PosReplayBatchDraft)
        self.assertIs(package.PosReplayEntryDraft, PosReplayEntryDraft)
        self.assertIs(package.PosReplaySummaryDraft, PosReplaySummaryDraft)
        self.assertIs(package.PosSimulatorAdapter, PosSimulatorAdapter)
        self.assertIs(package.build_pos_receipt_doc, build_pos_receipt_doc)
        self.assertIs(
            package.build_pos_replay_batch_doc,
            build_pos_replay_batch_doc,
        )
        self.assertIs(
            package.build_pos_replay_entry,
            build_pos_replay_entry,
        )
        self.assertIs(
            package.build_pos_replay_summary_doc,
            build_pos_replay_summary_doc,
        )
        self.assertIs(
            package.receipt_validation_blockers,
            receipt_validation_blockers,
        )
        self.assertIs(package.validate_pos_receipt, validate_pos_receipt)
        self.assertEqual(PosAdapter.__name__, "PosAdapter")
        self.assertEqual(
            FiscalReceiptCaptureDraft.__name__,
            "FiscalReceiptCaptureDraft",
        )
        self.assertEqual(PosReceiptLineDraft.__name__, "PosReceiptLineDraft")
        self.assertEqual(PosReceiptDraft.__name__, "PosReceiptDraft")
        self.assertEqual(PosReplayEntryDraft.__name__, "PosReplayEntryDraft")
        self.assertEqual(PosReplayBatchDraft.__name__, "PosReplayBatchDraft")
        self.assertEqual(
            PosReplaySummaryDraft.__name__,
            "PosReplaySummaryDraft",
        )
        self.assertEqual(PosSimulatorAdapter.__name__, "PosSimulatorAdapter")
        self.assertTrue(callable(build_pos_receipt_doc))
        self.assertTrue(callable(build_pos_replay_batch_doc))
        self.assertTrue(callable(build_pos_replay_entry))
        self.assertTrue(callable(build_pos_replay_summary_doc))
        self.assertTrue(callable(receipt_validation_blockers))
        self.assertTrue(callable(validate_pos_receipt))

    def test_simulator_adapter_builds_receipt_drafts_and_summary(self):
        """Ensure the simulator adapter builds proof-path replay data."""

        simulator = PosSimulatorAdapter(location="Sofia - POS")
        receipts = simulator.sample_receipts()
        receipt_draft = simulator.build_pos_receipt_doc(receipts[0])
        review_receipt_draft = simulator.build_pos_receipt_doc(receipts[1])
        replay_entry = simulator.build_pos_replay_entry(
            receipts[1],
            entry_id="ENTRY-2026-0001",
            queued_at="2026-05-13T10:20:00+03:00",
        )
        batch = simulator.build_pos_replay_batch_doc(
            batch_id="BATCH-2026-0001",
            receipts=receipts,
            received_on="2026-05-13T10:30:00+03:00",
            notes="POS proof run",
        )
        summary = simulator.build_pos_replay_summary_doc(batch)

        self.assertIsInstance(simulator, PosAdapter)
        self.assertEqual(2, len(receipts))
        self.assertEqual("R-2026-0001", receipt_draft.receipt_number)
        self.assertEqual("Sofia - POS", receipt_draft.location)
        self.assertEqual(1, receipt_draft.line_count())
        self.assertFalse(receipt_draft.needs_review())
        self.assertEqual("0001", receipt_draft.to_doc()["fiscal_number"])
        self.assertEqual(
            "APRP-ITEM-001", receipt_draft.receipt_lines[0].barcode
        )
        self.assertEqual("R-2026-0002", review_receipt_draft.receipt_number)
        self.assertTrue(review_receipt_draft.needs_review())
        self.assertEqual("Imported", review_receipt_draft.status)
        self.assertEqual("Requires Review", replay_entry.replay_state)
        self.assertEqual("Review Required", replay_entry.operator_state)
        self.assertTrue(replay_entry.review_required)
        self.assertEqual("Review Required", batch.operator_state)
        self.assertEqual("Ready", batch.status)
        self.assertEqual(2, batch.receipt_count)
        self.assertEqual(2, len(batch.receipts))
        self.assertEqual(2, len(batch.replay_entries))
        self.assertEqual(2, summary.receipt_count)
        self.assertEqual(2, summary.line_count)
        self.assertEqual(1, summary.pending_count)
        self.assertEqual(0, summary.posted_count)
        self.assertEqual(1, summary.fiscalized_count)
        self.assertEqual(0, summary.duplicate_receipt_count)
        self.assertEqual(1, summary.mismatch_receipt_count)
        self.assertEqual("Open", summary.blackout_state)
        self.assertTrue(summary.review_required)
        self.assertEqual("Review Required", summary.operator_state)
        self.assertFalse(summary.is_clear())

    def test_unsafe_receipts_stay_blocked(self):
        """Ensure invalid receipts stay blocked and do not replay silently."""

        bad_receipt = {
            "receipt_id": "R-2026-0003",
            "pos_id": "POS-1",
            "receipt_datetime": "2026-05-13T10:45:00+03:00",
            "payment_method": "cash",
            "customer_ref": "WEB-2026-0003",
            "operator_name": "ops",
            "declared_gross_eur": 0.0,
            "receipt_lines": [
                {
                    "barcode": "APRP-ITEM-003",
                    "quantity": 0,
                    "unit_price_eur": 5.0,
                    "warehouse": "Sofia - POS",
                }
            ],
        }

        blockers = receipt_validation_blockers(bad_receipt)
        receipt_draft = build_pos_receipt_doc(bad_receipt)
        replay_entry = build_pos_replay_entry(
            bad_receipt,
            entry_id="ENTRY-2026-0002",
            note="Review before posting",
        )
        batch = build_pos_replay_batch_doc(
            batch_id="BATCH-2026-0002",
            receipts=(bad_receipt,),
            notes="Blocked POS replay",
        )
        summary = build_pos_replay_summary_doc(batch)

        self.assertFalse(validate_pos_receipt(bad_receipt))
        self.assertIn("APRP-ITEM-003:invalid", blockers)
        self.assertEqual("Failed", receipt_draft.status)
        self.assertTrue(receipt_draft.needs_review())
        self.assertEqual("Failed", replay_entry.replay_state)
        self.assertEqual("Blocked", replay_entry.operator_state)
        self.assertTrue(replay_entry.validation_blockers)
        self.assertEqual("Failed", batch.status)
        self.assertEqual("Blocked", batch.operator_state)
        self.assertTrue(batch.review_required)
        self.assertFalse(batch.is_clear())
        self.assertEqual("Blocked", summary.operator_state)
        self.assertTrue(summary.review_required)
        self.assertFalse(summary.is_clear())

    def test_pos_service_methods_cover_symbol_paths(self):
        """Ensure the POS service methods stay explicit."""

        self.assertEqual(
            PosSimulatorAdapter.sample_receipts.__name__,
            "sample_receipts",
        )
        self.assertEqual(
            PosSimulatorAdapter.validate_receipt.__name__,
            "validate_receipt",
        )
        self.assertEqual(
            PosSimulatorAdapter.build_pos_receipt_doc.__name__,
            "build_pos_receipt_doc",
        )
        self.assertEqual(
            PosSimulatorAdapter.build_pos_replay_entry.__name__,
            "build_pos_replay_entry",
        )
        self.assertEqual(
            PosSimulatorAdapter.build_pos_replay_batch_doc.__name__,
            "build_pos_replay_batch_doc",
        )
        self.assertEqual(
            PosSimulatorAdapter.build_pos_replay_summary_doc.__name__,
            "build_pos_replay_summary_doc",
        )
        self.assertEqual(PosReceiptDraft.to_doc.__name__, "to_doc")
        self.assertEqual(PosReceiptDraft.to_contract.__name__, "to_contract")
        self.assertEqual(PosReceiptDraft.posting_date.__name__, "posting_date")
        self.assertEqual(PosReceiptLineDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            PosReceiptLineDraft.to_contract.__name__,
            "to_contract",
        )
        self.assertEqual(FiscalReceiptCaptureDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            FiscalReceiptCaptureDraft.to_contract.__name__,
            "to_contract",
        )
        self.assertEqual(PosReplayEntryDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            PosReplayEntryDraft.to_contract.__name__, "to_contract"
        )
        self.assertEqual(PosReplayBatchDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            PosReplayBatchDraft.to_contract.__name__, "to_contract"
        )
        self.assertEqual(PosReplaySummaryDraft.to_doc.__name__, "to_doc")
        self.assertEqual(
            PosReplaySummaryDraft.to_contract.__name__, "to_contract"
        )
