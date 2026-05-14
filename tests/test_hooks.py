"""APRP hooks contract tests."""

import unittest


class TestAprpHooks(unittest.TestCase):
    """Verify the Frappe hooks module stays wired to APRP."""

    def test_hooks_module_exposes_aprp_metadata(self):
        """Ensure the hooks module exposes the APRP app contract."""
        import aprp.hooks as hooks

        self.assertEqual("aprp", hooks.app_name)
        self.assertEqual("APRP", hooks.app_title)
        self.assertEqual("APRP", hooks.app_publisher)
        self.assertEqual(
            "Advanced Production Resource Planning",
            hooks.app_description,
        )
        self.assertEqual(["frappe", "erpnext"], hooks.required_apps)
        self.assertEqual("aprp.install.before_install", hooks.before_install)
        self.assertEqual("aprp.install.after_install", hooks.after_install)
        self.assertEqual("aprp.install.before_tests", hooks.before_tests)
