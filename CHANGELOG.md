# Changelog
**Doc ID:** CHANGELOG
**Doc Type:** changelog
**Project Version:** 0.4.0
**Project Stage:** beta
**Maintenance Stance:** active
**Compatibility Policy:** forward-only
**Versioning Mode:** versioned
**Last Updated:** 2026-05-12
**DevCovenant Version:** 1.0.1b5

<!-- DEVCOV:BEGIN -->
## DevCovenant Change Logging Rules
This opening section is managed by DevCovenant for repositories that
use DevCovenant.
Add one entry for each substantive change under the current version header.
Keep entries newest-first and record dates in ISO format (`YYYY-MM-DD`).
Each entry must include Change/Why/Impact summary lines with action verbs.
Keep one blank line after each version heading and between dated entries.
Example:
```
## Version 1.2.3

- 2026-01-23:
  Change: Fixed null-pointer crash in invoice import.
  Why: Production job failed when optional contact data was missing.
  Impact: Imports complete for records with partial contact details.
  Files:
  billing/imports/parser.py
  billing/imports/test_parser.py
  docs/imports.md
  Long paths should be wrapped with a trailing \
  backslash and continued on the next indented line.
  Example:
  services/customer/contact/normalization/\
    fallback_rules.py

- 2026-01-22:
  Change: Fixed duplicate email notifications on retry.
  Why: Retry worker re-enqueued already-confirmed notification events.
  Impact: Users receive one email per successful notification event.
  Files:
  notifications/worker.py
  notifications/retry.py
  notifications/test_retry.py

## Version 1.2.2

- 2026-01-21:
  Change: Added initial release for invoice import and notification flow.
  Why: Defined a first production-ready baseline for billing automation.
  Impact: Teams can import invoices and send notifications end-to-end.
  Files:
  billing/imports/parser.py
  notifications/worker.py
  CHANGELOG.md
```
<!-- DEVCOV:END -->

## APRP Version 0.4.0

- 2026-05-12:
  Change: Rewrote the README overview to present APRP directly as the product.
  Why: Keep the public front door in product terms instead of transitional or
    extraction language.
  Impact: The README now states APRP's contract without migration framing.
  Files:
  README.md

- 2026-05-12:
  Change: Materialized APRP governance, the version anchor, and the seeded
    profile stack.
  Why: Bootstrapped the public APRP repo from the installed DevCovenant
    contract so versioning, workflow, and docs can resolve from the repo
    itself.
  Impact: Enabled DevCovenant to regenerate APRP's managed docs, workflow,
    registry, and dependency artifacts from the repo contract.
  Files:
  README.md
  devcovenant/README.md
  devcovenant/config.yaml
  devcovenant/custom/profiles/github/assets/ci.yml
  devcovenant/custom/profiles/github/github.yaml
  devcovenant/custom/profiles/userproject/userproject.yaml
  devcovenant/registry/registry.yaml
  .github/workflows/ci.yml
  .gitignore
  .pre-commit-config.yaml
  AGENTS.md
  CHANGELOG.md
  CONTRIBUTING.md
  PLAN.md
  VERSION
  bandit.yaml
  licenses/README.md
  licenses/THIRD_PARTY_LICENSES.md
  licenses/build-1.4.4.txt
  licenses/cfgv-3.5.0.txt
  licenses/click-8.3.3.txt
  licenses/distlib-0.4.0.txt
  licenses/filelock-3.29.0.txt
  licenses/identify-2.6.19.txt
  licenses/iniconfig-2.3.0.txt
  licenses/nodeenv-1.10.0.txt
  licenses/packaging-26.2.txt
  licenses/pip-26.1.txt
  licenses/pip-tools-7.5.3.txt
  licenses/platformdirs-4.9.6.txt
  licenses/pluggy-1.6.0.txt
  licenses/pre_commit-4.6.0.txt
  licenses/Pygments-2.20.0.txt
  licenses/pyproject_hooks-1.2.0.txt
  licenses/pytest-9.0.3.txt
  licenses/python-discovery-1.2.2.txt
  licenses/PyYAML-6.0.3.txt
  licenses/semver-3.0.4.txt
  licenses/setuptools-82.0.1.txt
  licenses/virtualenv-21.2.4.txt
  licenses/wheel-0.47.0.txt
  pyproject.toml
  requirements.in
  requirements.lock
