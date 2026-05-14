"""Install validation and repository hygiene checks for APRP."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import yaml

FRAPPE_DOCTYPES = (
    (
        "APRP Product",
        "aprp_product",
        False,
        (
            "product_name",
            "internal_id",
            "barcode",
            "supplier",
            "tax_profile",
            "price_list",
            "sellable",
            "publishable",
            "notes",
        ),
    ),
    (
        "APRP Supplier",
        "aprp_supplier",
        False,
        (
            "supplier_name",
            "vat_id",
            "email",
            "phone",
            "country",
            "default_vat_rate",
            "notes",
        ),
    ),
    (
        "APRP Customer",
        "aprp_customer",
        False,
        (
            "customer_name",
            "phone",
            "email",
            "delivery_address",
            "country",
            "notes",
        ),
    ),
    (
        "APRP Location",
        "aprp_location",
        False,
        (
            "location_name",
            "company",
            "warehouse",
            "address",
            "notes",
        ),
    ),
    (
        "APRP Warehouse Policy",
        "aprp_warehouse_policy",
        False,
        (
            "policy_name",
            "location",
            "warehouse",
            "purpose",
            "priority",
            "active",
            "notes",
        ),
    ),
    (
        "APRP Tax Profile",
        "aprp_tax_profile",
        False,
        (
            "tax_profile_name",
            "country",
            "vat_rate",
            "sales_vat_rate",
            "purchase_vat_rate",
            "notes",
        ),
    ),
    (
        "APRP Price List",
        "aprp_price_list",
        False,
        (
            "price_list_name",
            "currency",
            "customer_group",
            "territory",
            "notes",
        ),
    ),
    (
        "APRP Pack Family",
        "aprp_pack_family",
        False,
        (
            "family_name",
            "unit_product",
            "box_product",
            "case_product",
            "pallet_product",
            "units_per_box",
            "boxes_per_case",
            "cases_per_pallet",
            "notes",
        ),
    ),
    (
        "APRP Product Profile",
        "aprp_product_profile",
        False,
        (
            "profile_name",
            "product",
            "supplier",
            "tax_profile",
            "price_list",
            "barcode",
            "description",
            "publishable",
            "notes",
        ),
    ),
    (
        "APRP Supplier SKU Mapping",
        "aprp_supplier_sku_mapping",
        False,
        ("supplier", "product", "sku", "barcode", "notes"),
    ),
    (
        "APRP Location Policy",
        "aprp_location_policy",
        False,
        (
            "policy_name",
            "location",
            "warehouse",
            "purpose",
            "priority",
            "active",
            "notes",
        ),
    ),
    (
        "APRP Intake Session",
        "aprp_intake_session",
        False,
        (
            "naming_series",
            "expense_id",
            "status",
            "posting_date",
            "location",
            "warehouse",
            "supplier",
            "operator",
            "confirm_scanned_quantities",
            "confirm_ready_to_post",
            "notes",
            "lines",
        ),
    ),
    (
        "APRP Intake Line",
        "aprp_intake_line",
        True,
        (
            "supplier_sku",
            "raw_name",
            "barcode",
            "product",
            "invoice_line_number",
            "quantity",
            "pack_role",
            "confirmed",
            "notes",
        ),
    ),
    (
        "APRP Unresolved Barcode",
        "aprp_unresolved_barcode",
        False,
        (
            "naming_series",
            "status",
            "barcode",
            "quantity",
            "location",
            "warehouse",
            "reason",
            "resolved_product",
            "resolved_by",
            "resolved_on",
            "pack_family_draft",
        ),
    ),
    (
        "APRP Storefront Sync Batch",
        "aprp_storefront_sync_batch",
        False,
        (
            "batch_id",
            "storefront_host",
            "status",
            "started_on",
            "finished_on",
            "catalog_rows",
            "order_rows",
            "notes",
            "events",
        ),
    ),
    (
        "APRP Storefront Sync Event",
        "aprp_storefront_sync_event",
        True,
        (
            "event_type",
            "source_ref",
            "product_profile",
            "sync_status",
            "notes",
        ),
    ),
    (
        "APRP POS Receipt",
        "aprp_pos_receipt",
        True,
        (
            "receipt_number",
            "location",
            "posting_date",
            "cashier",
            "customer",
            "grand_total",
            "currency",
            "fiscal_number",
            "source_system",
            "status",
            "notes",
        ),
    ),
    (
        "APRP POS Replay Batch",
        "aprp_pos_replay_batch",
        False,
        (
            "batch_id",
            "location",
            "status",
            "received_on",
            "receipt_count",
            "notes",
            "receipts",
        ),
    ),
    (
        "APRP Courier Adapter",
        "aprp_courier_adapter",
        False,
        ("adapter_name", "service_name", "endpoint_url", "active", "notes"),
    ),
    (
        "APRP Courier Shipment",
        "aprp_courier_shipment",
        False,
        (
            "shipment_no",
            "adapter",
            "order_reference",
            "tracking_number",
            "destination_location",
            "customer",
            "cod_amount",
            "status",
            "notes",
            "events",
        ),
    ),
    (
        "APRP Courier Event",
        "aprp_courier_event",
        True,
        ("event_code", "event_status", "event_time", "location_text", "notes"),
    ),
    (
        "APRP Integration Log",
        "aprp_integration_log",
        False,
        (
            "integration_name",
            "operation",
            "direction",
            "reference_doctype",
            "reference_name",
            "status",
            "message",
            "payload_hash",
            "notes",
        ),
    ),
)


class TestAprpInstallValidation(unittest.TestCase):
    """Verify generalized install profiles and repo hygiene."""

    def test_opsconfig_accepts_variant_profile(self):
        """Ensure opsconfig renders an arbitrary valid config variant."""
        example = yaml.safe_load(
            Path("ops/opsconfig.yaml.example").read_text(encoding="utf-8")
        )
        variant = deepcopy(example)
        variant.update(
            {
                "app_name": "aprp-variant",
                "backend_host": "backend-variant.example.invalid",
                "mirror_host": "mirror-variant.example.invalid",
                "backend_site_name": "site-variant.example.invalid",
                "contact_email": "ops-variant@example.invalid",
                "db_host": "proxysql-variant",
                "deploy_git_remote": "upstream",
                "deploy_git_branch": "develop",
                "backup_remote": "variant-b2",
            }
        )
        variant["galera_cluster_members"] = [
            "backend-variant.example.invalid",
            "mirror-variant.example.invalid",
        ]
        variant["galera_primary_host"] = "backend-variant.example.invalid"
        variant["galera_mirror_host"] = "mirror-variant.example.invalid"

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "opsconfig.yaml"
            config_path.write_text(
                yaml.safe_dump(variant, sort_keys=False),
                encoding="utf-8",
            )

            primary = subprocess.run(
                [
                    "python3",
                    "ops/opsconfig.py",
                    "primary",
                    "--config",
                    str(config_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            mirror = subprocess.run(
                [
                    "python3",
                    "ops/opsconfig.py",
                    "mirror",
                    "--config",
                    str(config_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            deploy = subprocess.run(
                [
                    "python3",
                    "ops/opsconfig.py",
                    "deploy",
                    "--config",
                    str(config_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            backup = subprocess.run(
                [
                    "python3",
                    "ops/opsconfig.py",
                    "backup",
                    "--config",
                    str(config_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

        self.assertIn("export APRP_APP_NAME=aprp-variant", primary)
        self.assertIn(
            "export APRP_BACKEND_HOST=backend-variant.example.invalid",
            primary,
        )
        self.assertIn(
            "export APRP_GALERA_CLUSTER_MEMBERS="
            "backend-variant.example.invalid,mirror-variant.example.invalid",
            primary,
        )
        self.assertIn("export APRP_GALERA_NODE=db-mirror", mirror)
        self.assertIn("export DEPLOY_GIT_REMOTE=upstream", deploy)
        self.assertIn("export DEPLOY_GIT_BRANCH=develop", deploy)
        self.assertIn(
            "export DEPLOY_SITE_NAME=site-variant.example.invalid",
            deploy,
        )
        self.assertIn("export BACKUP_RCLONE_REMOTE=variant-b2", backup)
        self.assertIn(
            "export BACKUP_SITE_NAME=site-variant.example.invalid",
            backup,
        )

    def test_frappe_app_surface_exists(self):
        """Ensure the installable app surface is present in the tree."""
        self.assertTrue(Path("aprp/hooks.py").is_file())
        self.assertTrue(Path("aprp/install.py").is_file())
        self.assertTrue(Path("aprp/modules.txt").is_file())
        self.assertTrue(Path("aprp/patches.txt").is_file())
        self.assertTrue(Path("aprp/aprp/doctype").is_dir())
        self.assertTrue(Path("aprp/aprp/doctype/__init__.py").is_file())

    def test_install_hooks_are_callable(self):
        """Ensure the install hook entrypoints stay importable."""
        import aprp.install as install

        self.assertTrue(callable(install.before_install))
        self.assertTrue(callable(install.after_install))
        self.assertTrue(callable(install.before_tests))

    def test_frappe_doctype_scaffold_matches_manifest(self):
        """Ensure each APRP DocType exists and exposes the expected shape."""
        doctype_root = Path("aprp/aprp/doctype")

        for name, folder, is_table, field_order in FRAPPE_DOCTYPES:
            doc_dir = doctype_root / folder
            json_path = doc_dir / f"{folder}.json"
            py_path = doc_dir / f"{folder}.py"
            init_path = doc_dir / "__init__.py"

            self.assertTrue(doc_dir.is_dir(), folder)
            self.assertTrue(json_path.is_file(), folder)
            self.assertTrue(py_path.is_file(), folder)
            self.assertTrue(init_path.is_file(), folder)

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            fields = tuple(field["fieldname"] for field in payload["fields"])

            self.assertEqual(name, payload["name"])
            self.assertEqual("APRP", payload["module"])
            self.assertEqual("DocType", payload["doctype"])
            self.assertEqual(bool(is_table), bool(payload["istable"]))
            self.assertEqual(list(field_order), payload["field_order"])
            self.assertEqual(field_order, fields)
            self.assertGreater(len(fields), 0)

    def test_repo_surface_has_no_banned_identity_or_secret_markers(self):
        """Ensure the product surfaces stay clear of banned strings."""
        surface_patterns = [
            "README.md",
            "SPEC.md",
            "PLAN.md",
            "docs/**/*.md",
            "ops/**/*.py",
            "ops/**/*.sh",
            "ops/**/*.yaml",
            "ops/**/*.yml",
            "ops/**/*.json",
            "caddy/Caddyfile",
            "compose*.yaml",
            ".github/workflows/*.yml",
            "aprp/**/*.py",
        ]
        collected = []
        seen = set()
        for pattern in surface_patterns:
            for path in Path(".").glob(pattern):
                if not path.is_file() or path in seen:
                    continue
                seen.add(path)
                collected.append(path.read_text(encoding="utf-8"))

        combined = "\n".join(collected)
        for banned in [
            r"\bGCV\b",
            r"\bgoblin\b",
            r"\bcard\b",
            r"\bbooster\b",
            r"\bTCG\b",
            "BEGIN PRIVATE KEY",
            "ghp_",
            "xox[baprs]-",
        ]:
            self.assertNotRegex(combined, banned)
