"""Tests for the APRP POS Replay Batch DocType controller."""

import importlib
import unittest


class TestAprpPosReplayBatchDocType(unittest.TestCase):
    """Verify the APRP POS Replay Batch controller module imports cleanly."""

    def test_imports(self):
        """Ensure the controller module stays importable."""
        module = importlib.import_module(
            "aprp.aprp.doctype.aprp_pos_replay_batch.aprp_pos_replay_batch"
        )
        self.assertIn("APRP", module.__doc__ or "")
