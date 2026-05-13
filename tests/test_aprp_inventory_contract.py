"""Core APRP inventory contract tests."""

import unittest
from pathlib import Path

from aprp.aprp import (
    IntakeLine,
    IntakeSession,
    InventorySafetyGate,
    PackFamily,
    StockOperation,
    UnresolvedBarcode,
    WarehousePolicy,
    WarehousePolicySet,
)


class TestAprpInventoryContract(unittest.TestCase):
    """Verify the inventory and packaging model stays explicit."""

    def test_pack_family_converts_tiers_into_units(self):
        """Ensure pack families keep unit, box, and case tiers explicit."""
        family = PackFamily(
            name="Demo Family",
            unit_item="Unit Item",
            box_item="Box Item",
            case_item="Case Item",
            units_per_box=12,
            boxes_per_case=6,
        )

        self.assertEqual(("Unit", "Box", "Case"), family.pack_roles())
        self.assertEqual(24, family.units_for("Box", 2))
        self.assertEqual(72, family.units_for("Case", 1))
        self.assertTrue(family.has_sealed_tier("Case"))

    def test_warehouse_policy_set_resolves_location_purpose(self):
        """Ensure location policy picks the explicit warehouse by purpose."""
        policy_set = WarehousePolicySet(
            policies=(
                WarehousePolicy(
                    policy_name="sofia-fulfillment",
                    location="Sofia",
                    warehouse="Sofia - Fulfillment",
                    purpose="Fulfillment",
                    priority=1,
                ),
                WarehousePolicy(
                    policy_name="sofia-reserve",
                    location="Sofia",
                    warehouse="Sofia - Reserve",
                    purpose="Reserve",
                    priority=1,
                ),
                WarehousePolicy(
                    policy_name="sofia-intake",
                    location="Sofia",
                    warehouse="Sofia - Intake",
                    purpose="Intake",
                    priority=1,
                ),
            ),
        )

        self.assertEqual(
            "Sofia - Fulfillment",
            policy_set.warehouse_for("Sofia", "Fulfillment"),
        )
        self.assertEqual(
            "Sofia - Reserve",
            policy_set.warehouse_for("Sofia", "Reserve"),
        )
        self.assertEqual(
            "Sofia - Intake",
            policy_set.warehouse_for("Sofia", "Intake"),
        )

    def test_intake_session_requires_confirmed_lines(self):
        """Ensure barcode-first intake stays staged before posting."""
        line = IntakeLine(
            supplier_sku="SKU-1",
            raw_name="Sample Item",
            barcode="1234567890123",
            quantity=2,
            confirmed=True,
        )
        session = IntakeSession(
            session_id="INTAKE-2026-0001",
            warehouse="Sofia - Intake",
            posting_date="2026-05-13",
            confirm_scanned_quantities=True,
            confirm_ready_to_post=True,
            lines=(line,),
        )

        self.assertTrue(line.is_ready())
        self.assertTrue(session.is_ready_to_post())
        self.assertEqual((line,), session.ready_lines())

    def test_unresolved_barcode_and_safety_gate_block_unsafe_sales(self):
        """Ensure unknown stock states remain visible and block unsafe use."""
        unresolved = UnresolvedBarcode(
            barcode="9999999999999",
            warehouse="Sofia - Intake",
        )
        gate = InventorySafetyGate(
            stock_known=False,
            stock_consistent=False,
            pack_family_known=True,
            policy_resolved=True,
            reservation_state_known=False,
        )
        operation = StockOperation(
            operation="transfer",
            item="APRP Product",
            quantity=1,
            source_warehouse="Sofia - Reserve",
            target_warehouse="Sofia - Fulfillment",
        )

        self.assertFalse(unresolved.is_resolved())
        self.assertFalse(gate.can_sell())
        self.assertFalse(gate.can_publish())
        self.assertIn("stock_known", gate.missing_requirements())
        self.assertIn("stock_consistent", gate.missing_requirements())
        self.assertIn("reservation_state_known", gate.missing_requirements())
        self.assertTrue(operation.requires_source())
        self.assertTrue(operation.requires_target())

    def test_inventory_docs_cover_the_pack_and_policy_model(self):
        """Ensure the inventory guide names the inventory contract."""
        inventory = Path("docs/inventory.md").read_text(encoding="utf-8")

        for token in [
            "aprp.aprp.inventory_contract",
            "Pack Family",
            "Intake Session",
            "Unresolved Barcode",
            "Inventory Safety Gate",
        ]:
            self.assertIn(token, inventory)
