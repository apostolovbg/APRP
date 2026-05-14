"""Runtime service helper tests for APRP."""

from __future__ import annotations

import hashlib
import importlib
import unittest
from pathlib import Path

import aprp.aprp as package
from aprp.aprp import IntakeLine as ContractIntakeLine
from aprp.aprp import (
    IntakeLineDraft,
    IntakeSessionDraft,
    IntegrationLogEntryDraft,
    InventorySafetyGate,
    ProductProfileDraft,
    SupplierSkuMappingDraft,
    UnresolvedBarcodeDraft,
    add_intake_line,
    block_unsafe_intake_session,
    build_integration_log_entry,
    build_product_profile_doc,
    build_supplier_sku_mapping_doc,
    detect_unresolved_barcode,
    intake_session_blockers,
    open_intake_session,
    post_safe_intake_session,
    product_publishability_blockers,
    validate_product_publishability,
)


class TestAprpRuntimeServices(unittest.TestCase):
    """Verify the runtime service helpers stay coherent."""

    def test_package_exports_runtime_service_helpers(self):
        """Ensure the package exposes the runtime service layer."""

        module = importlib.import_module("aprp.aprp.runtime_services")
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")

        self.assertIn("APRP", module.__doc__ or "")
        self.assertIn("aprp.aprp.runtime_services", readme)
        self.assertIn("aprp.aprp.runtime_services", spec)
        self.assertIs(package.ProductProfileDraft, ProductProfileDraft)
        self.assertIs(package.IntakeLineDraft, IntakeLineDraft)
        self.assertIs(package.IntakeSessionDraft, IntakeSessionDraft)
        self.assertIs(
            package.IntegrationLogEntryDraft, IntegrationLogEntryDraft
        )
        self.assertIs(package.SupplierSkuMappingDraft, SupplierSkuMappingDraft)
        self.assertIs(package.UnresolvedBarcodeDraft, UnresolvedBarcodeDraft)
        self.assertIs(
            package.build_product_profile_doc, build_product_profile_doc
        )
        self.assertIs(
            package.build_supplier_sku_mapping_doc,
            build_supplier_sku_mapping_doc,
        )
        self.assertIs(package.open_intake_session, open_intake_session)
        self.assertIs(package.add_intake_line, add_intake_line)
        self.assertIs(
            package.block_unsafe_intake_session,
            block_unsafe_intake_session,
        )
        self.assertIs(
            package.detect_unresolved_barcode, detect_unresolved_barcode
        )
        self.assertIs(
            package.build_integration_log_entry,
            build_integration_log_entry,
        )
        self.assertTrue(callable(ProductProfileDraft.from_input))
        self.assertTrue(callable(SupplierSkuMappingDraft.from_input))
        self.assertTrue(callable(IntakeLineDraft.from_input))
        self.assertTrue(callable(IntakeSessionDraft.from_input))
        self.assertTrue(callable(IntegrationLogEntryDraft.from_input))

    def test_product_profile_builder_respects_publishability_gate(self):
        """Ensure product profiles only publish when the gate is healthy."""

        safe_gate = InventorySafetyGate(
            stock_known=True,
            stock_consistent=True,
            pack_family_known=True,
            policy_resolved=True,
        )
        unsafe_gate = InventorySafetyGate(
            stock_known=False,
            stock_consistent=True,
            pack_family_known=True,
            policy_resolved=True,
        )
        profile = ProductProfileDraft(
            profile_name="Fruit Profile",
            product="APRP Product",
            supplier="APRP Supplier",
            tax_profile="BG VAT",
            price_list="Retail",
            barcode="1234567890123",
            description="Fresh fruit profile",
            publishable=True,
        )

        doc = build_product_profile_doc(profile, safety_gate=safe_gate)

        self.assertEqual("Fruit Profile", doc["profile_name"])
        self.assertTrue(doc["publishable"])
        self.assertTrue(
            validate_product_publishability(profile, safety_gate=safe_gate)
        )
        self.assertFalse(
            validate_product_publishability(profile, safety_gate=unsafe_gate)
        )
        self.assertIn(
            "stock_known",
            product_publishability_blockers(
                profile,
                safety_gate=unsafe_gate,
            ),
        )

    def test_supplier_mapping_builder_normalizes_doc(self):
        """Ensure supplier SKU mappings stay DocType-shaped."""

        draft = SupplierSkuMappingDraft(
            supplier="APRP Supplier",
            product="APRP Product",
            sku="SKU-123",
            barcode="1234567890123",
            notes="Primary mapping",
        )

        doc = build_supplier_sku_mapping_doc(draft)

        self.assertEqual("APRP Supplier", doc["supplier"])
        self.assertEqual("APRP Product", doc["product"])
        self.assertEqual("SKU-123", doc["sku"])
        self.assertEqual("1234567890123", doc["barcode"])
        self.assertEqual("Primary mapping", doc["notes"])

    def test_intake_session_helpers_open_add_and_post_safe_sessions(self):
        """Ensure intake sessions open, collect lines, and post safely."""

        session = open_intake_session(
            expense_id="INTAKE-2026-0001",
            warehouse="Sofia - Intake",
            posting_date="2026-05-13",
            location="Sofia",
            supplier="APRP Supplier",
            operator="ops",
            confirm_scanned_quantities=True,
            confirm_ready_to_post=True,
        )
        line = ContractIntakeLine(
            supplier_sku="SKU-1",
            raw_name="Sample Item",
            barcode="1234567890123",
            item="APRP Product",
            quantity=2,
            pack_role="Unit",
            confirmed=True,
        )

        session = add_intake_line(session, line)

        self.assertEqual("Ready", session.status)
        self.assertTrue(session.is_ready_to_post())
        self.assertEqual(1, session.line_count())
        self.assertEqual(1, session.ready_line_count())
        self.assertEqual((), intake_session_blockers(session))
        posted = post_safe_intake_session(session)

        self.assertEqual("Posted", posted.status)

    def test_block_unsafe_session_and_detect_unresolved_barcode(self):
        """Ensure unsafe intake stays blocked and unmapped barcodes surface."""

        unsafe_session = open_intake_session(
            expense_id="INTAKE-2026-0002",
            warehouse="Sofia - Intake",
            posting_date="2026-05-13",
            location="Sofia",
            supplier="APRP Supplier",
            operator="ops",
        )
        unsafe_session = add_intake_line(
            unsafe_session,
            {
                "supplier_sku": "SKU-2",
                "raw_name": "Unknown Item",
                "barcode": "9999999999999",
                "quantity": 1,
                "pack_role": "Unit",
                "confirmed": False,
            },
        )

        blockers = intake_session_blockers(unsafe_session)
        blocked = block_unsafe_intake_session(unsafe_session)
        unresolved = detect_unresolved_barcode(
            ContractIntakeLine(
                supplier_sku="SKU-2",
                raw_name="Unknown Item",
                barcode="9999999999999",
                item="",
                quantity=1,
                pack_role="Unit",
                confirmed=False,
            ),
            location="Sofia",
            warehouse="Sofia - Intake",
        )

        self.assertIn("confirm_scanned_quantities", blockers)
        self.assertIn("confirm_ready_to_post", blockers)
        self.assertIn("SKU-2:confirmed", blockers)
        self.assertEqual("Cancelled", blocked.status)
        self.assertIn("Blocked:", blocked.notes)
        self.assertIsNotNone(unresolved)
        self.assertEqual("9999999999999", unresolved.barcode)
        self.assertEqual("Sofia", unresolved.location)
        self.assertEqual("Sofia - Intake", unresolved.warehouse)
        self.assertEqual("Unknown", unresolved.reason)

    def test_integration_log_entry_hashes_payload(self):
        """Ensure integration log entries hash payloads deterministically."""

        entry = build_integration_log_entry(
            integration_name="APRP Intake",
            operation="post",
            direction="Outbound",
            reference_doctype="APRP Intake Session",
            reference_name="INTAKE-2026-0001",
            payload={"b": 2, "a": 1},
        )

        self.assertEqual(
            hashlib.sha256(b'{"a":1,"b":2}').hexdigest(),
            entry["payload_hash"],
        )

    def test_runtime_service_class_methods_cover_symbol_paths(self):
        """Ensure the class-level service helpers stay explicit."""

        profile = ProductProfileDraft.from_input(
            {
                "profile_name": "Fruit Profile",
                "product": "APRP Product",
                "supplier": "APRP Supplier",
                "tax_profile": "BG VAT",
                "price_list": "Retail",
                "barcode": "1234567890123",
                "publishable": True,
            }
        )
        mapping = SupplierSkuMappingDraft.from_input(
            {
                "supplier": "APRP Supplier",
                "product": "APRP Product",
                "sku": "SKU-4",
                "barcode": "1234567890123",
            }
        )
        line = IntakeLineDraft.from_input(
            {
                "supplier_sku": "SKU-4",
                "raw_name": "Sample Item",
                "barcode": "1234567890123",
                "product": "APRP Product",
                "quantity": 1,
                "pack_role": "Unit",
                "confirmed": True,
            }
        )
        session = IntakeSessionDraft.from_input(
            {
                "expense_id": "INTAKE-2026-0003",
                "warehouse": "Sofia - Intake",
                "posting_date": "2026-05-13",
                "confirm_scanned_quantities": True,
                "confirm_ready_to_post": True,
            }
        )
        unresolved = UnresolvedBarcodeDraft(
            barcode="9999999999999",
            location="Sofia",
            warehouse="Sofia - Intake",
            quantity=1,
        )
        log_entry = IntegrationLogEntryDraft.from_input(
            {
                "integration_name": "APRP Intake",
                "operation": "post",
                "payload": {"b": 2, "a": 1},
            }
        )

        session = session.with_line(line)

        self.assertEqual("APRP Product", profile.to_doc()["product"])
        self.assertEqual("SKU-4", mapping.to_doc()["sku"])
        self.assertTrue(line.is_ready())
        self.assertEqual(1, session.line_count())
        self.assertEqual("Ready", session.status)
        self.assertFalse(unresolved.is_resolved())
        self.assertEqual("9999999999999", unresolved.to_doc()["barcode"])
        self.assertEqual("Pending", log_entry.to_doc()["status"])
        self.assertEqual(
            hashlib.sha256(b'{"a":1,"b":2}').hexdigest(),
            log_entry.to_doc()["payload_hash"],
        )
