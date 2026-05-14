# Release Summary
**Doc ID:** RELEASE
**Doc Type:** release-summary
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP is at the 1.0.0 production-grade and demo-ready release-candidate
checkpoint. The repository now carries an installable ERPNext/Frappe
application, config-first runtime assets, safe showcase handling, and
repo-owned deploy, backup, and mirror operations.

This summary records what the current code base supports and what remains
intentionally out of scope.

## Release Summary

- `aprp.aprp.runtime_services` bridges product profiles, intake, and
  integration logs into DocType drafts.
- `aprp.aprp.storefront_services` bridges storefront sync, order ingest,
  and WooCommerce proof paths.
- `aprp.aprp.showcase_services` bridges demo-only seed, reset, and
  disposable public proof flows.
- `aprp.aprp.pos_services` bridges POS and Datecs replay paths.
- `aprp.aprp.courier_services` bridges courier and COD adapter
  boundaries.
- `aprp.aprp.accounting_services` bridges reviewable operational
  accounting summaries.
- `ops/opsconfig.yaml` drives non-secret install and runtime config.
- `docs/system.md` documents deploy, backup, restore, mirror, and health
  checks.

## Known Limitations

- Full business integration work is quoted separately.
- Paid billing, full multi-tenant automation, and unrestricted anonymous
  ERP access are not included.
- Some adapter shells remain proof-path implementations rather than full
  vendor integrations.
- Public storefront and showcase surfaces are controlled boundaries, not
  ERP administration.
- Real secrets stay on the deployment host or in untracked env files.

## Validation

- Python tests pass with `python3 -m unittest discover -v`.
- Python files compile with `python3 -m compileall -q aprp tests`.
- Shell scripts pass `bash -n` checks in the test suite.
- Compose validation runs where Docker is available.
- DevCovenant gate, workflow, and audit commands pass in this repo.

If a check is blocked by local dependencies, that block must remain
documented and honest before release.
