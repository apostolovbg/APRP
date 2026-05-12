# Development Plan
**Doc ID:** PLAN
**Doc Type:** plan
**Project Version:** 0.4.0
**Project Stage:** beta
**Maintenance Stance:** active
**Compatibility Policy:** forward-only
**Versioning Mode:** versioned
**Last Updated:** 2026-05-12
**DevCovenant Version:** 1.0.1b5

<!-- DEVCOV:BEGIN -->
This opening section is managed by DevCovenant.
Use `PLAN.md` to track active implementation work below this block.
<!-- DEVCOV:END -->

Use this plan to track active implementation work.
Keep slices dependency-ordered, concrete, and current.

## Table of Contents
1. [Overview](#overview)
2. [How Slices Are Executed](#how-slices-are-executed)
3. [Execution Slices](#execution-slices)
4. [Validation Routine](#validation-routine)

## Overview
- APRP is the public product and this plan is its execution ledger.
- The legacy repo is the technical reference for implementation details
  and is named only here.
- This plan turns the APRP generalization work into ordered slices so
  the repo can become its own working system.
- The immediate target is to finish the debranding surface, then the
  primary runtime, then the mirror, then deploy and recovery, then
  verification and freeze.

## How Slices Are Executed
- Each slice means a complete end-to-end implementation pass, not a
  partial triage note.
- Keep the scope of one slice inside the files named in that slice.
- Update the slice status in the same session when work lands.
- Do not start later slices before earlier dependency slices are complete.
- Use `CHANGELOG.md` to record the slice outcome when behavior or
  governance changes.
- Use `devcovenant gate --open`, `devcovenant gate --verify`,
  `devcovenant run`, and `devcovenant gate --close` around each
  completed slice.

## Execution Slices
1. [not done] Slice 0 - Debrand and normalize the repo surface.
   Depends on:
   - none
   Contract sources:
   - README.md
   - SPEC.md
   - PLAN.md
   - docs/**
   - existing package and module names
   Work to do:
   - Replace legacy identity and client-specific wording with APRP language.
   - Rewrite public docs so they read as APRP product docs, not transition notes.
   - Rename package and module names where needed so imports and test names match APRP naming.
   - Remove or rename tests, fixtures, and generated artifacts that leak legacy identity.
   - Keep the legacy repo reference limited to this PLAN.md.
   Done when:
   - README, SPEC, and PLAN describe APRP without public legacy naming.
   - The repo surface is debranded enough that runtime work can proceed without identity drift.
   - No legacy identity strings remain outside this plan's internal reference note.

2. [not done] Slice 1 - Build the primary runtime and deterministic bootstrap.
   Depends on:
   - Slice 0
   Surfaces:
   - compose.yaml
   - Dockerfile
   - caddy/
   - ops/site_setup.sh
   - ops/backend_entrypoint.sh
   - ops/deploy.sh
   - ops/backup.sh
   - docs/system.md
   - runtime tests
   Work to do:
   - Build the primary container runtime for backend, reverse proxy, Redis, and database.
   - Make site bootstrap deterministic from a fresh empty volume.
   - Use `kuche.aprp.store` as the backend host and `aprp.store` as the public edge.
   - Make the same bootstrap path work in local, deploy, and CI.
   - Keep backend login reachable from a clean startup.
   Done when:
   - A fresh stack can bootstrap the site, install the app, and migrate from one repo-owned path.
   - The backend responds on the expected hostname and port.
   - Bootstrap failure modes are visible and documented.

3. [not done] Slice 2 - Separate the mirror as its own deployment unit.
   Depends on:
   - Slice 1
   Surfaces:
   - compose.mirror.yaml
   - mirror entrypoints and scripts
   - recovery helpers
   - runtime docs
   Work to do:
   - Give the mirror its own lifecycle, volumes, and network surface.
   - Make `kotka.aprp.store` the mirror host.
   - Keep mirror state mutually agnostic from the primary stack.
   - Provide restore, reseed, and rejoin steps without manual repair.
   - Keep the design open to more than one mirror container per host.
   Done when:
   - Primary and mirror can be started and stopped independently.
   - Mirror state does not depend on the primary stack being local.
   - Recovery and rejoin steps are documented and rehearsed.

4. [not done] Slice 3 - Wire storefront and public routing.
   Depends on:
   - Slice 1
   Surfaces:
   - storefront config
   - public routing
   - browser-facing docs
   Work to do:
   - Bring up the storefront on `aprp.store`.
   - Keep the storefront as a sales surface, not the ERP brain.
   - Ensure public site traffic lands in an ERP-backed catalog and checkout flow.
   - Keep operator preview separate from public launch posture.
   Done when:
   - Reviewers can browse the storefront from the public hostname.
   - Storefront actions land in the ERP-backed flow.
   - Public exposure is explicit and documented.

5. [not done] Slice 4 - Wire deploy, backup, and recovery to the same bootstrap path.
   Depends on:
   - Slice 1
   - Slice 2
   Surfaces:
   - ops/deploy.sh
   - ops/backup.sh
   - recovery helpers
   - operator docs
   Work to do:
   - Make deploy and backup call the same deterministic bootstrap contract.
   - Ensure backups capture database, files, and site config consistently.
   - Make restore and mirror-based recovery deterministic and documented.
   - Keep offsite retention and secret handling explicit.
   Done when:
   - Deploy does not need a second ad hoc bootstrap path.
   - Backups and restore rehearsals pass from repo-owned scripts.
   - Recovery paths are documented and repeatable.

6. [not done] Slice 5 - Verify, clean, and freeze the baseline.
   Depends on:
   - Slices 0-4
   Surfaces:
   - tests
   - changelog
   - DevCovenant registry and runtime artifacts
   - hygiene scans
   Work to do:
   - Run the full DevCovenant cycle.
   - Add or update tests covering bootstrap, mirror separation, and public-doc hygiene.
   - Scan for banned identity strings and secrets.
   - Freeze the debranding baseline once all slices are closed.
   Done when:
   - Gates pass cleanly.
   - No legacy identity remains outside the permitted reference note in this plan.
   - The repo is ready for the next implementation cycle without policy drift.

## Validation Routine
- Verify tests pass for the active slice.
- Verify generated artifacts synchronize after refresh.
- Verify documentation and changelog are updated where behavior changed.
- Verify `devcovenant check` passes after the slice closes.
