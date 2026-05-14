"""Showcase service helper tests for APRP."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

import aprp.aprp as package
from aprp.aprp import (
    SHOWCASE_CONTROLLED_ACTIONS,
    SHOWCASE_PUBLIC_DEMO_CHECKLIST,
    SHOWCASE_RESET_STEPS,
    SHOWCASE_SCREENSHARE_CHECKLIST,
    SHOWCASE_SESSION_COOKIE_NAME,
    ShowcaseDemoRecord,
    ShowcaseResetPlan,
    ShowcaseSeedPlan,
    build_showcase_reset_plan,
    build_showcase_seed_plan,
    controlled_demo_actions,
    mark_demo_only_record,
    public_demo_checklist,
    screenshare_demo_checklist,
)


class TestAprpShowcaseServices(unittest.TestCase):
    """Verify the safe showcase service layer stays explicit."""

    def test_package_exports_showcase_service_helpers(self):
        """Ensure the package exposes the showcase service layer."""

        module = importlib.import_module("aprp.aprp.showcase_services")
        readme = Path("README.md").read_text(encoding="utf-8")
        spec = Path("SPEC.md").read_text(encoding="utf-8")
        docs = Path("docs/showcase.md").read_text(encoding="utf-8")

        self.assertIn("APRP", module.__doc__ or "")
        self.assertIn("aprp.aprp.showcase_services", readme)
        self.assertIn("aprp.aprp.showcase_services", spec)
        self.assertIn("docs/showcase.md", readme)
        self.assertIn("docs/showcase.md", spec)
        self.assertIn("aprp.aprp.showcase_services", docs)
        self.assertIs(package.ShowcaseDemoRecord, ShowcaseDemoRecord)
        self.assertIs(package.ShowcaseResetPlan, ShowcaseResetPlan)
        self.assertIs(package.ShowcaseSeedPlan, ShowcaseSeedPlan)
        self.assertIs(
            package.ShowcaseDemoRecord.to_doc,
            ShowcaseDemoRecord.to_doc,
        )
        self.assertIs(
            package.ShowcaseResetPlan.to_doc,
            ShowcaseResetPlan.to_doc,
        )
        self.assertIs(
            package.ShowcaseSeedPlan.to_doc,
            ShowcaseSeedPlan.to_doc,
        )
        self.assertIs(
            package.build_showcase_reset_plan, build_showcase_reset_plan
        )
        self.assertIs(
            package.build_showcase_seed_plan, build_showcase_seed_plan
        )
        self.assertIs(package.controlled_demo_actions, controlled_demo_actions)
        self.assertIs(package.mark_demo_only_record, mark_demo_only_record)
        self.assertIs(package.public_demo_checklist, public_demo_checklist)
        self.assertIs(
            package.screenshare_demo_checklist,
            screenshare_demo_checklist,
        )
        self.assertEqual(
            module.SHOWCASE_SESSION_COOKIE_NAME,
            SHOWCASE_SESSION_COOKIE_NAME,
        )
        self.assertEqual(
            module.SHOWCASE_CONTROLLED_ACTIONS,
            SHOWCASE_CONTROLLED_ACTIONS,
        )
        self.assertEqual(
            module.SHOWCASE_PUBLIC_DEMO_CHECKLIST,
            SHOWCASE_PUBLIC_DEMO_CHECKLIST,
        )
        self.assertEqual(module.SHOWCASE_RESET_STEPS, SHOWCASE_RESET_STEPS)
        self.assertEqual(
            module.SHOWCASE_SCREENSHARE_CHECKLIST,
            SHOWCASE_SCREENSHARE_CHECKLIST,
        )

    def test_showcase_seed_and_reset_plans_partition_demo_state(self):
        """Ensure the showcase seed and reset paths stay separated."""

        seed_plan = build_showcase_seed_plan(
            public_host="aprp.store",
            backend_host="kuche.aprp.store",
        )
        reset_plan = build_showcase_reset_plan(seed_plan)
        overlap_ref = seed_plan.demo_record_refs()[0]

        self.assertEqual("aprp.store", seed_plan.public_host)
        self.assertEqual("kuche.aprp.store", seed_plan.backend_host)
        self.assertEqual(
            SHOWCASE_SESSION_COOKIE_NAME,
            seed_plan.session_cookie_name,
        )
        self.assertGreater(len(seed_plan.catalog_rows), 0)
        self.assertEqual(1, len(seed_plan.order_rows))
        self.assertTrue(seed_plan.order_rows[0].https_only)
        self.assertIn(
            f"{SHOWCASE_SESSION_COOKIE_NAME}:disposable",
            seed_plan.order_rows[0].public_session_id,
        )
        self.assertTrue(
            all(record.demo_only for record in seed_plan.demo_records)
        )
        self.assertTrue(
            all(record.resettable for record in seed_plan.demo_records)
        )
        self.assertEqual(
            SHOWCASE_CONTROLLED_ACTIONS,
            seed_plan.controlled_actions,
        )
        self.assertEqual(SHOWCASE_RESET_STEPS, reset_plan.reset_steps)
        self.assertIsInstance(reset_plan, ShowcaseResetPlan)
        self.assertEqual(seed_plan.demo_records, reset_plan.demo_records)

        with self.assertRaises(ValueError):
            build_showcase_reset_plan(
                seed_plan,
                production_record_refs=(overlap_ref,),
            )

    def test_showcase_checklists_cover_boundary_language(self):
        """Ensure the checklists keep the public boundary explicit."""

        public_checklist = public_demo_checklist()
        screenshare_checklist = screenshare_demo_checklist()
        marker = mark_demo_only_record("Order", "SHOWCASE-ORDER-001")

        self.assertIn("anonymous", " ".join(public_checklist).lower())
        self.assertIn("disposable", " ".join(public_checklist).lower())
        self.assertIn("reset", " ".join(public_checklist).lower())
        self.assertIn("https", " ".join(public_checklist).lower())
        self.assertIn("hidden", " ".join(screenshare_checklist).lower())
        self.assertIn("reset", " ".join(screenshare_checklist).lower())
        self.assertIn("https", " ".join(screenshare_checklist).lower())
        self.assertTrue(marker.demo_only)
        self.assertTrue(marker.resettable)
        self.assertEqual("Disposable", marker.session_scope)
