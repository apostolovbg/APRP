# Changelog
**Doc ID:** CHANGELOG
**Doc Type:** changelog
**Project Version:** 0.4.0
**Project Stage:** beta
**Maintenance Stance:** active
**Compatibility Policy:** forward-only
**Versioning Mode:** versioned
**Last Updated:** 2026-05-13
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

- 2026-05-13:
  Change: Removed the demo/public-showcase surface, rewrote the plan and
    spec toward the generalized ERP/ops baseline, and simplified the
    runtime to backend-first config-driven routing.
  Why: Aligned APRP with the installable system baseline and deferred
    user-viewable storefront rollout to a later plan.
  Impact: Documented the backend/mirror framework baseline without the
    demo landing page/docs; the current docs, tests, and runtime code
    now describe the generalized backend/mirror framework only.
  Files:
  CHANGELOG.md
  PLAN.md
  README.md
  SPEC.md
  caddy/Caddyfile
  caddy/Dockerfile
  caddy/public/index.html
  compose.yaml
  docs/security.md
  docs/showcase.md
  docs/storefront.md
  docs/system.md
  ops/opsconfig.py
  ops/opsconfig.yaml
  ops/opsconfig.yaml.example
  tests/test_aprp_baseline.py
  tests/test_aprp_runtime.py
  tests/test_opsconfig.py
  tests/test_public_showcase.py

- 2026-05-13:
  Change: Implemented Slice 4 storefront and public routing with a
    config-driven HTTPS landing page, reviewer hand-off, and safe
    public surface tests.
  Why: Preserved APRP's config-first boundary while preventing
    hardcoded hostnames and public ERP admin exposure.
  Impact: Locked in a public showcase page, config-driven reviewer
    login routing, and docs/tests for the safe public surface.
  Files:
  CHANGELOG.md
  PLAN.md
  README.md
  SPEC.md
  caddy/Caddyfile
  caddy/Dockerfile
  caddy/public/index.html
  compose.yaml
  docs/security.md
  docs/showcase.md
  docs/storefront.md
  docs/system.md
  ops/opsconfig.py
  ops/opsconfig.yaml
  ops/opsconfig.yaml.example
  tests/test_aprp_runtime.py
  tests/test_opsconfig.py
  tests/test_public_showcase.py

- 2026-05-13:
  Change: Marked Slice 3 done in PLAN.md after centralizing APRP's
    non-secret runtime config in `ops/opsconfig.yaml` and adding the
    renderer smoke tests.
  Why: Record completion of the generalized config contract before the
    next runtime slice starts.
  Impact: APRP now records the tracked ops config example and the
    untracked instance file as the completed generalized wiring slice.
  Files:
  CHANGELOG.md
  PLAN.md

- 2026-05-13:
  Change: Centralized APRP's non-secret runtime configuration in
    `ops/opsconfig.yaml`, added a dedicated renderer test, and rewired
    the runtime surfaces to consume the exported config values.
  Why: Consolidate the config-first runtime contract into one tracked
    source of truth while keeping secrets in separate env files.
  Impact: APRP now derives its public, internal, deploy, backup, and
    mirror wiring from the example-plus-instance config pair instead of
    split JSON files and hardcoded runtime defaults.
  Files:
  CHANGELOG.md
  PLAN.md
  README.md
  SPEC.md
  compose.mirror.yaml
  compose.yaml
  docs/system.md
  ops/backup.sh
  ops/backup_config.json
  ops/deploy.sh
  ops/deploy_config.json
  ops/deploy_mirror.sh
  ops/env.mirror.example
  ops/env.primary.example
  ops/opsconfig.py
  ops/opsconfig.yaml
  ops/opsconfig.yaml.example
  ops/site_setup.sh
  tests/test_aprp_runtime.py
  tests/test_opsconfig.py

- 2026-05-13:
  Change: Centralized APRP's non-secret runtime configuration in
    `ops/opsconfig.yaml`, added the YAML renderer, and rewired the
    runtime surfaces to consume the exported config values.
  Why: Consolidate the config-first runtime contract into one tracked
    source of truth while keeping secrets in separate env files.
  Impact: APRP now derives its public, internal, deploy, and backup
    wiring from the example-plus-instance config pair instead of split
    JSON files and hardcoded runtime defaults.
  Files:
  CHANGELOG.md
  README.md
  SPEC.md
  PLAN.md
  compose.yaml
  docs/system.md
  ops/deploy.sh
  ops/opsconfig.py
  ops/opsconfig.yaml.example
  tests/test_aprp_runtime.py

- 2026-05-13:
  Change: Removed concrete host literals from compose, Caddy, runtime,
    and doc surfaces, and switched the public edge to config-driven
    host variables.
  Why: Ensure APRP stays config-first so non-config files remain
    reusable across installations instead of carrying a one-off demo
    address set.
  Impact: APRP now normalizes host routing and enforces the generalized
    host contract in docs and tests.
  Files:
  CHANGELOG.md
  README.md
  aprp/hooks.py
  caddy/Caddyfile
  compose.mirror.yaml
  compose.yaml
  ops/backup.sh
  ops/backup_config.json
  ops/deploy.sh
  ops/deploy_config.json
  ops/deploy_mirror.sh
  ops/env.mirror.example
  ops/env.primary.example
  ops/site_setup.sh
  tests/test_aprp_baseline.py
  tests/test_aprp_runtime.py

- 2026-05-13:
  Change: Reworked PLAN.md and SPEC.md to mark HTTPS, storefront,
    reviewer access, deploy, backup, and mirror recovery as first-class
    APRP targets and to forbid hardcoded hostnames in compose or other
    non-config files.
  Why: Aligned APRP with a config-first framework model so the public
    surfaces are product behavior, not demo-only wiring.
  Impact: APRP now documents config-only host wiring, first-class
    public surfaces, and a concrete profile that stays last in the
    validation order.
  Files:
  CHANGELOG.md
  PLAN.md
  SPEC.md

- 2026-05-13:
  Change: Rewrote PLAN.md around generalized config-driven runtime slices
    and updated SPEC.md for smoke-tested installs and optional GitHub
    wrappers.
  Why: Aligned APRP with a framework-first model where local config and
    secrets define the install and the concrete demo remains the final
    operational check.
  Impact: APRP now documents smoke-testable generalized wiring,
    host-managed secrets by default, and a demo-last validation path.
  Files:
  CHANGELOG.md
  PLAN.md
  SPEC.md

- 2026-05-12:
  Change: Updated PLAN.md and SPEC.md around HTTPS public demo access,
    reviewer demo scope, and generated workflow wrappers.
  Why: Aligned the repo docs with a user-testable storefront demo and
    repo-owned operator scripts instead of a hidden-account model.
  Impact: Added HTTPS-only public entrypoints, scoped reviewer access,
    and generated non-CI workflow wrappers to the docs.
  Files:
  CHANGELOG.md
  PLAN.md
  SPEC.md

- 2026-05-12:
  Change: Replaced the temporary demo config with a tracked ops config
    example and updated the docs and plan around the instance config
    shape.
  Why: Aligned APRP's concrete-installation model with a tracked
    example file and an untracked local config file.
  Impact: APRP now documents `ops/opsconfig.yaml.example` as the repo
    contract while keeping installation-specific values local.
  Files:
  CHANGELOG.md
  PLAN.md
  SPEC.md
  docs/system.md
  ops/opsconfig.yaml.example
  tests/test_aprp_baseline.py
  tests/test_aprp_runtime.py
  .gitignore
  ops/demo_config.json

- 2026-05-12:
  Change: Added a tracked concrete-demo profile and rewrote future plan
    and spec slices around config-driven hostnames.
  Why: Aligned APRP's future work with a reusable framework layer
    instead of hardcoded demo addresses.
  Impact: Enabled future slices to consume `ops/demo_config.json` for
    repo-specific demo settings, and the runtime tests cover that
    tracked profile.
  Files:
  CHANGELOG.md
  PLAN.md
  SPEC.md
  ops/demo_config.json
  tests/test_aprp_runtime.py

- 2026-05-12:
  Change: Implemented the APRP mirror host on its own network and
    recovery commands.
  Why: Aligned mirror lifecycle and rebuild steps with the primary
    stack.
  Impact: APRP now documents and tests mirror restore, reseed, and
    rejoin paths independently.
  Files:
  CHANGELOG.md
  PLAN.md
  compose.mirror.yaml
  docs/system.md
  ops/db_mirror_restore.sh
  ops/deploy_mirror.sh
  tests/test_aprp_runtime.py

- 2026-05-12:
  Change: Revised PLAN.md to clear the remaining line-length warnings.
  Why: Aligned the execution ledger with the repository's documented
    line-length policy.
  Impact: Enabled the plan to pass DevCovenant checks without warning
    noise.
  Files:
  CHANGELOG.md
  PLAN.md

- 2026-05-12:
  Change: Implemented the APRP backend startup path through
    `ops/site_setup.sh`.
  Why: Aligned local and deploy startup with the same deterministic site
    setup contract.
  Impact: Enabled fresh backend volumes to reach a ready site before
    `bench serve`.
  Files:
  CHANGELOG.md
  PLAN.md
  docs/system.md
  ops/backend_entrypoint.sh
  tests/test_aprp_runtime.py

- 2026-05-12:
  Change: Marked Slice 0 done in PLAN.md after validating APRP docs.
  Why: Align the execution ledger with the finished debranding pass.
  Impact: Record Slice 0 completion without widening repo scope.
  Files:
  PLAN.md
  CHANGELOG.md

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
  Why: Build the primary and mirror container contract for the configured
    backend and mirror hosts without depending on the old pilot
    repository.
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
