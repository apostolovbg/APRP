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

## Log changes here

## Version 0.4.0

- 2026-05-12:
  Change: Rewrote PLAN.md to define APRP execution slices and working
    order.
  Why: Align implementation planning with runtime, mirror, deploy, and
    verification work.
  Impact: Enables APRP to carry a dependency-ordered plan without generic
    placeholder text.
  Files:
  PLAN.md
  CHANGELOG.md

- 2026-05-12:
  Change: Completed the APRP README with the remaining public sections and
    closed the showcase example fence.
  Why: Keep the public root document aligned with the documented section map
    and the new runtime guide link.
  Impact: APRP now presents a complete front door for the runtime and
    documentation slice.
  Files:
  README.md
  CHANGELOG.md

- 2026-05-12:
  Change: Added the APRP runtime stack scaffold, package-scoped dependency
    artifacts, and the repo-owned bootstrap scripts.
  Why: Build the primary and mirror container contract for `kuche.aprp.store`
    and `kotka.aprp.store` without depending on the old pilot repository.
  Impact: APRP can now bootstrap its runtime, mirror, deploy, and backup
    surfaces from its own repo layout.
  Files:
  aprp/__init__.py
  aprp/hooks.py
  aprp/modules.txt
  aprp/patches.txt
  aprp/aprp/__init__.py
  aprp/public/__init__.py
  aprp/templates/__init__.py
  aprp/templates/pages/__init__.py
  aprp/licenses/README.md
  aprp/licenses/THIRD_PARTY_LICENSES.md
  aprp/runtime-requirements.lock
  compose.yaml
  compose.mirror.yaml
  Dockerfile
  caddy/Dockerfile
  caddy/Caddyfile
  garbd/Dockerfile
  docs/system.md
  ops/backend_entrypoint.sh
  ops/backup.sh
  ops/backup_config.json
  ops/db_mirror_restore.sh
  ops/deploy.sh
  ops/deploy_config.json
  ops/deploy_mirror.sh
  ops/env.mirror.example
  ops/env.primary.example
  ops/garbd_entrypoint.sh
  ops/galera_mysqld_base.cnf
  ops/mariadb_galera_entrypoint.sh
  ops/proxysql_entrypoint.sh
  ops/rclone.conf.example
  ops/site_setup.sh
  ops/socketio_entrypoint.sh
  tests/test_aprp_runtime.py
  tests/test_hooks.py
  .gitignore

- 2026-05-12:
  Change: Added a neutral APRP baseline sanity test package so `unittest`
    discovers a real run target.
  Why: Prevent `devcovenant run` from failing on an empty test tree while
    keeping the coverage APRP-only.
  Impact: The gate workflow can record its required run without introducing
    legacy identity checks.
  Files:
  tests/__init__.py
  tests/test_aprp_baseline.py
  CHANGELOG.md

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
