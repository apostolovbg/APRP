"""Frappe hooks for APRP."""

import os

app_name = "aprp"
app_title = "APRP"
app_publisher = "APRP"
app_description = "Advanced Production Resource Planning"
app_email = os.environ.get("APRP_APP_EMAIL", "ops@example.invalid")
app_license = "GPL-3.0-only"
add_to_apps_screen = []
