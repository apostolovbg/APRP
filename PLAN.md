# Development Plan
**Doc ID:** PLAN
**Doc Type:** plan
**Project Version:** 0.4.0
**Project Stage:** beta
**Maintenance Stance:** active
**Compatibility Policy:** forward-only
**Versioning Mode:** versioned
**Last Updated:** 2026-05-13
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
- APRP is a generalized, config-driven framework layer first.
- All non-secret runtime config lives in `ops/opsconfig.yaml`; env files
  are secrets and machine-local auth only.
- That YAML file also carries the internal service hostnames, ports,
  and URLs used by the runtime stack.
- HTTPS, storefront integration, deploy, backup, and mirror recovery
  are first-class APRP targets.
- The tracked `ops/opsconfig.yaml.example` defines the installation
  shape; a local `ops/opsconfig.yaml` instance supplies the actual
  values for each environment.
- The repo must stay downloadable and user-testable from checkout with
  the tracked example config plus local secrets.
- Wiring must be smoke-testable against any valid configuration.
- Hardcoded hostnames and public URLs do not belong in compose files or
  other non-config artifacts.
- `ci.yml` stays DevCovenant-managed; non-CI GitHub workflows are
  generated wrappers around repo-owned scripts.
- User-viewable storefront rollout work belongs in a later plan after
  the generalized framework baseline is complete.
- The immediate target is to finish the debranding surface, then the
  generalized runtime, then the mirror, then the tracked ops config
  example, then deploy and recovery, then generated workflow wrappers,
  then the generalized baseline freeze.

## How Slices Are Executed
- Each slice means a complete end-to-end implementation pass, not a
  partial triage note.
- Keep the scope of one slice inside the files named in that slice.
- Update the slice status in the same session when work lands.
- Do not start later slices before earlier dependency slices are complete.
- Concrete installation settings belong in tracked `ops/` config, not
  hardcoded in reusable runtime code or docs.
- The repo-owned scripts translate `ops/opsconfig.yaml` into the shell
  environment before Compose, Caddy, deploy, or backup run.
- Public hostnames, mirror members, and other environment-specific
  addresses belong in tracked config or local instance files, not in
  compose files or other non-config artifacts.
- Repo-owned scripts are the source of truth for deploy, backup, and
  mirror bootstrap; generated workflow wrappers must stay in sync.
- GitHub-hosted orchestration is optional and must not become the trust
  anchor for local installs.
- Use `CHANGELOG.md` to record the slice outcome when behavior or
  governance changes.
- Use `devcovenant gate --open`, `devcovenant gate --verify`,
  `devcovenant run`, and `devcovenant gate --close` around each
  completed slice.

## Execution Slices
1. [done] Slice 0 - Debrand and normalize the repo surface.
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
   - Rewrite public docs so they read as APRP product docs, not
     transition notes.
   - Rename package and module names where needed so imports and test
     names match APRP naming.
   - Remove or rename tests, fixtures, and generated artifacts that
     leak legacy identity.
   - Keep the legacy repo reference limited to this PLAN.md.
   Done when:
   - README, SPEC, and PLAN describe APRP without public legacy
     naming.
   - The repo surface is debranded enough that runtime work can
     proceed without identity drift.
   - No legacy identity strings remain outside this plan's internal
     reference note.

2. [not done] Slice 1 - Build the generalized runtime and deterministic
   bootstrap.
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
   - Build the primary container runtime for backend, reverse proxy, Redis,
     and database.
   - Make site bootstrap deterministic from a fresh empty volume.
- Make the same bootstrap path work in local, deploy, CI, and any
  valid installation profile.
- Keep backend login reachable from a clean startup.
- Smoke-test the runtime wiring against config-driven hostnames and
  secrets instead of a single hardcoded profile.
- Remove hardcoded hostnames and public URLs from compose files and
  other non-config runtime artifacts.
   Done when:
   - A fresh stack can bootstrap the site, install the app, and migrate
     from one repo-owned path.
   - The backend responds on the configured hostname and port.
   - Bootstrap failure modes are visible and documented.
   - The runtime passes smoke tests on a generalized config profile.

3. [done] Slice 2 - Separate the mirror as its own deployment unit.
   Depends on:
   - Slice 1
   Surfaces:
   - compose.mirror.yaml
   - mirror entrypoints and scripts
   - recovery helpers
   - runtime docs
   Work to do:
   - Give the mirror its own lifecycle, volumes, and network surface.
   - Make the mirror host and cluster membership config-driven.
   - Keep mirror state mutually agnostic from the primary stack.
   - Provide restore, reseed, and rejoin steps without manual repair.
   - Keep the design open to more than one mirror container per host.
   Done when:
   - Primary and mirror can be started and stopped independently.
   - Mirror state does not depend on the primary stack being local.
   - Recovery and rejoin steps are documented and rehearsed.
   - Additional mirror members can be added by configuration.

4. [done] Slice 3 - Track the repo ops config example and smoke-test
   generalized wiring.
   Depends on:
   - Slice 1
   - Slice 2
   Surfaces:
   - ops/opsconfig.yaml.example
   - untracked ops/opsconfig.yaml
   - runtime and smoke tests
   - docs/system.md
   Work to do:
   - Keep the tracked example config and the local instance config in
     the same shape.
   - Make `ops/opsconfig.yaml` the source of truth for all non-secret
     runtime config.
   - Make bench, WordPress, WooCommerce, deploy, backup, and mirror
     wiring read the instance config instead of hardcoding addresses in
     compose files or other non-config artifacts.
  - Add smoke tests that verify generalized wiring against config and
     secrets.
   - Keep secrets and machine-local overrides in untracked env files.
   Done when:
   - The tracked example and local instance config share the same keys
     and sections.
   - Future runtime, storefront, deploy, and recovery steps consume the
     config shape instead of hardcoded strings.
   - Smoke tests prove that APRP works with a valid generic config
     before any later storefront rollout is introduced.

5. [done] Slice 4 - Wire storefront integration with scoped access.
   Depends on:
   - Slice 1
   - Slice 3
   Surfaces:
   - storefront config
   - storefront integration
   - runtime docs
   Work to do:
   - Bring up the storefront on the configured public host over HTTPS.
   - Keep public visitors on storefront-safe actions and provide scoped
     access for ERP-backed flows.
   - Keep the storefront as a sales surface, not the ERP brain.
   - Ensure public site traffic lands in an ERP-backed catalog and
     checkout flow.
   - Keep operator preview separate from public launch posture.
   Done when:
   - Public users can browse the storefront from the configured public
     host over HTTPS.
   - Storefront actions land in the ERP-backed flow.
   - Public exposure is explicit and documented.
   - Anonymous users cannot reach ERP admin surfaces.
   - Scoped credentials stay limited and resettable.

6. [not done] Slice 5 - Wire deploy, backup, recovery, and workflow
   wrappers to the same bootstrap path.
   Depends on:
   - Slice 1
   - Slice 2
   - Slice 3
   Surfaces:
   - ops/deploy.sh
   - ops/backup.sh
   - recovery helpers
   - generated GitHub workflow wrappers
   - operator docs
   Work to do:
   - Make deploy and backup call the same deterministic bootstrap contract.
   - Generate non-CI GitHub workflow wrappers from repo-owned scripts;
     keep `ci.yml` DevCovenant-managed.
   - Ensure backups capture database, files, and site config consistently.
   - Make restore and mirror-based recovery deterministic and documented.
   - Keep offsite retention and secret handling explicit.
   - Prefer local or host-managed secrets for deploy, backup, and mirror
     operations; GitHub orchestration stays optional.
   Done when:
   - Deploy does not need a second ad hoc bootstrap path.
   - Generated workflow wrappers stay in sync with repo-owned scripts.
   - Backups and restore rehearsals pass from repo-owned scripts.
   - Recovery paths are documented and repeatable.
   - Local operation works without GitHub-hosted operational secrets.

7. [not done] Slice 6 - Validate the concrete operational profile and
   freeze the baseline.
   Depends on:
   - Slices 0-5
   Surfaces:
   - tests
   - changelog
   - DevCovenant registry and runtime artifacts
   - hygiene scans
   - generalized install validation config
   Work to do:
   - Run the full DevCovenant cycle.
   - Apply the generalized installation profile as the last acceptance
     check for the APRP stack.
   - Add or update tests covering bootstrap, mirror separation, the
     tracked ops config example, generalized smoke wiring, and
     public-doc hygiene.
   - Scan for banned identity strings and secrets.
   - Freeze the baseline only after the generalized installation
     profile passes.
   Done when:
   - Gates pass cleanly.
   - The generalized install works with arbitrary valid config.
   - The generalized installation profile passes as the final
     operational check.
   - No legacy identity remains outside the permitted reference note in
     this plan.
   - The repo is ready for the next implementation cycle without policy
     drift.

## Validation Routine
- Verify tests pass for the active slice.
- Verify generated artifacts synchronize after refresh.
- Verify documentation and changelog are updated where behavior changed.
- Verify generated workflow wrappers stay aligned with repo-owned
  scripts.
- Verify the generalized install works against smoke-tested config
  profiles.
- Verify hardcoded hostnames and public URLs do not remain in compose
  files or other non-config artifacts.
- Verify `devcovenant check` passes after the slice closes.
