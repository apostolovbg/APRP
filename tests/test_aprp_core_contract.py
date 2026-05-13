"""Core APRP business contract tests."""

import unittest
from pathlib import Path

from aprp.aprp import (
    CORE_DOCTYPES,
    MODULE_NAME,
    PERMISSION_DOMAINS,
    WORKSPACE_SECTIONS,
    DoctypeContract,
    PermissionDomain,
    WorkspaceSection,
    core_doctype_names,
    permission_domain_names,
    workspace_names,
)


class TestAprpCoreContract(unittest.TestCase):
    """Verify the core business model stays explicit in the app."""

    def test_core_doctypes_cover_the_business_core(self):
        """Ensure the app contract names the core master-data surfaces."""
        self.assertEqual("APRP", MODULE_NAME)
        self.assertEqual(
            (
                "APRP Product",
                "APRP Supplier",
                "APRP Customer",
                "APRP Location",
                "APRP Warehouse Policy",
                "APRP Tax Profile",
                "APRP Price List",
            ),
            core_doctype_names(),
        )
        self.assertEqual(7, len(CORE_DOCTYPES))
        self.assertIsInstance(CORE_DOCTYPES[0], DoctypeContract)

        product = CORE_DOCTYPES[0]
        self.assertIn("internal_id", product.fields)
        self.assertIn("product_name", product.fields)
        self.assertIn("barcode", product.fields)
        self.assertIn("supplier", product.fields)
        self.assertIn("tax_profile", product.fields)
        self.assertIn("price_list", product.fields)

    def test_permission_domains_remain_explicit(self):
        """Ensure the app contract keeps the permission boundaries named."""
        self.assertEqual(
            (
                "operator",
                "staff",
                "location-scoped-user",
            ),
            permission_domain_names(),
        )
        self.assertEqual(3, len(PERMISSION_DOMAINS))
        self.assertIsInstance(PERMISSION_DOMAINS[0], PermissionDomain)
        self.assertIn("APRP Operator", PERMISSION_DOMAINS[0].roles)
        self.assertIn("APRP Staff", PERMISSION_DOMAINS[1].roles)
        self.assertIn("APRP Location User", PERMISSION_DOMAINS[2].roles)

    def test_workspace_sections_cover_the_initial_navigation(self):
        """Ensure the workspace contract keeps the navigation explicit."""
        self.assertEqual(
            (
                "Inventory",
                "Purchasing",
                "Operations",
            ),
            workspace_names(),
        )
        self.assertEqual(3, len(WORKSPACE_SECTIONS))
        self.assertIsInstance(WORKSPACE_SECTIONS[0], WorkspaceSection)

        inventory = WORKSPACE_SECTIONS[0]
        purchasing = WORKSPACE_SECTIONS[1]
        operations = WORKSPACE_SECTIONS[2]

        self.assertIn("APRP Product", inventory.doctypes)
        self.assertIn("APRP Warehouse Policy", inventory.doctypes)
        self.assertIn("APRP Supplier", purchasing.doctypes)
        self.assertIn("APRP Tax Profile", purchasing.doctypes)
        self.assertIn("APRP Customer", operations.doctypes)

    def test_docs_cover_the_core_contract(self):
        """Ensure the product docs explain the same core contract."""
        inventory = Path("docs/inventory.md").read_text(encoding="utf-8")
        purchasing = Path("docs/purchasing.md").read_text(encoding="utf-8")

        for token in [
            "APRP Product",
            "APRP Location",
            "APRP Warehouse Policy",
            "APRP Customer",
        ]:
            self.assertIn(token, inventory)

        for token in [
            "APRP Supplier",
            "APRP Tax Profile",
            "APRP Price List",
            "APRP Customer",
        ]:
            self.assertIn(token, purchasing)
