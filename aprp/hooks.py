"""Frappe hooks for APRP."""

import os

app_name = "aprp"
app_title = "APRP"
app_publisher = "APRP"
app_description = "Advanced Production Resource Planning"
app_email = os.environ.get("APRP_APP_EMAIL", "ops@example.invalid")
app_license = "GPL-3.0-only"
required_apps = ["frappe", "erpnext"]
add_to_apps_screen = []
before_install = "aprp.install.before_install"
after_install = "aprp.install.after_install"
before_tests = "aprp.install.before_tests"
