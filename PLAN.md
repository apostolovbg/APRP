# Development Plan
**Doc ID:** PLAN
**Doc Type:** plan
**Project Version:** 0.4.0
**Project Stage:** beta
**Maintenance Stance:** active
**Compatibility Policy:** forward-only
**Versioning Mode:** versioned
**Last Updated:** 2026-05-14
**DevCovenant Version:** 1.0.1b5

<!-- DEVCOV:BEGIN -->
This opening section is managed by DevCovenant.
Use `PLAN.md` to track active implementation work below this block.
<!-- DEVCOV:END -->

Use this plan to track active implementation work.

Keep slices dependency-ordered, concrete, current, and runtime-focused.

## Table of Contents

1. [Overview](#overview)
2. [How Slices Are Executed](#how-slices-are-executed)
3. [Execution Slices](#execution-slices)
4. [Validation Routine](#validation-routine)

## Overview

* APRP is a config-driven ERPNext operational system for Bulgarian
  commerce, inventory, procurement, storefront, POS, courier, and COD
  workflows.
* The current repository is a governed beta foundation. It has real
  contracts, DocType surfaces, services, tests, docs, and ops assets.
* This plan exists to make the beta marker true as a usable SaaS-style
  product, not merely a strong codebase.
* The target is **1.0.0 beta-SaaS readiness**.
* Beta-SaaS readiness means APRP can be installed, configured, shown,
  operated, backed up, restored, validated, and quoted for real business
  integration work.
* The system must support ERP-owned truth, one blind WooCommerce
  storefront, multi-location physical sites, packaging relations, POS
  and fiscal capture boundaries, courier adapters, COD, returns, demo
  mode, and recoverable operations.
* Public endpoints, demo domains, mirror members, and environment
  addresses belong in tracked config or local instance config, not in
  reusable runtime code.
* Non-secret runtime config stays in `ops/opsconfig.yaml`.
* Secrets stay outside the repository.
* Repo-owned scripts remain the contract for install, deploy, backup,
  restore, mirror, health checks, and release rehearsal.
* Public documentation must be sharp, honest, and free of private
  implementation history.
* APRP must be able to support a public storefront, a controlled ERP
  showcase, and a commercial call-to-action for full business integration
  quotes.

Beta-SaaS readiness does not mean unrestricted public self-service
production onboarding.

Beta-SaaS readiness does mean a serious operator can install the system,
run a showcase, demonstrate ERP-to-storefront cause and effect, and start
paid implementation work from a reproducible base.

## How Slices Are Executed

* Each slice means a complete implementation pass, not a note.
* Each slice must leave code, tests, docs, and changelog evidence where
  behavior changed.
* Do not mark a slice done unless the relevant checks support it.
* Do not treat contract-only behavior as runtime completion.
* Do not polish UI before install, runtime, and validation work.
* Do not add secrets, database dumps, private keys, private data, or
  real credentials.
* Do not publish previous-business identity, private history, or
  implementation narrative.
* Do not hardcode public hostnames in reusable runtime code.
* Concrete installation settings belong in tracked `ops/` config or
  local instance config.
* Repo-owned scripts translate `ops/opsconfig.yaml` into the shell
  environment before runtime, deploy, backup, restore, or mirror work.
* Public showcase behavior must never weaken production security
  assumptions.
* Anonymous visitors must not receive unrestricted ERP administration.
* Simulators are acceptable for beta if adapter boundaries are clear and
  real credentials are not required in tests.
* Use `CHANGELOG.md` to record slice outcomes when behavior,
  documentation, or governance changes.
* Use the configured local governance workflow around each completed
  slice.
* Keep every slice small enough to review, but complete enough to run.

## Execution Slices

1. [open] Slice 1 - Rebaseline the current beta.

   Depends on:

   * current repository state

   Surfaces:

   * `README.md`
   * `SPEC.md`
   * `PLAN.md`
   * `CHANGELOG.md`
   * `pyproject.toml`
   * `aprp/`
   * `tests/`
   * `docs/`
   * `ops/`
   * CI configuration

   Scope:

   * Inspect the current repo after the first full implementation pass.
   * Identify what is runtime-real, simulated, shell-only, or
     documentation-only.
   * Align project stage as beta across public docs.
   * Replace overclaims with beta-SaaS language.
   * Ensure no private implementation history appears in public docs.
   * Ensure public hostnames live in config or approved public docs only.
   * Ensure no private data or real secrets are present.
   * Ensure the current test count and limitations are documented
     honestly.

   Done when:

   * the repo has a clear beta baseline;
   * public docs no longer overclaim production maturity;
   * known limitations are explicit;
   * hygiene checks pass;
   * the next runtime slice is selected.

2. [open] Slice 2 - Prove fresh ERPNext installation.

   Depends on:

   * Slice 1

   Surfaces:

   * app metadata
   * hooks
   * modules
   * patches
   * fixtures
   * DocType JSON
   * workspace records
   * install tests
   * install docs

   Scope:

   * Verify APRP installs as a real ERPNext/Frappe app.
   * Fix app metadata, hooks, module definitions, and fixtures as
     needed.
   * Ensure DocType JSON files are valid and loadable.
   * Add or fix workspace/module navigation.
   * Add install validation tests that do not depend on live secrets.
   * Document the exact local install path.

   Done when:

   * a fresh bench-style install path is documented;
   * app imports are clean;
   * hooks load cleanly;
   * required DocTypes exist and validate;
   * install tests pass where local dependencies allow;
   * failure modes are documented honestly.

3. [open] Slice 3 - Harden the ERP business runtime.

   Depends on:

   * Slice 2

   Surfaces:

   * product profile services
   * supplier SKU services
   * location policy services
   * intake services
   * unresolved barcode services
   * integration log services
   * permission fixtures
   * tests

   Scope:

   * Connect contract objects to real runtime service behavior.
   * Ensure product publishability checks are enforced.
   * Ensure unsafe stock cannot become sellable.
   * Ensure unknown barcodes enter review state.
   * Ensure intake sessions can open, receive lines, block unsafe
     posting, and post safe data.
   * Ensure integration logs are written consistently.
   * Ensure permission domains support operator, staff, and admin
     responsibilities.

   Done when:

   * core runtime services operate against real or testable Frappe
     surfaces;
   * unsafe paths are tested;
   * publish-blocking behavior is tested;
   * integration logging is tested;
   * permissions are represented clearly.

4. [open] Slice 4 - Make adapter architecture real.

   Depends on:

   * Slice 3

   Surfaces:

   * storefront adapters
   * POS adapters
   * courier adapters
   * accounting exporters
   * adapter registry
   * adapter config
   * simulator implementations
   * tests

   Scope:

   * Consolidate adapter boundaries into a predictable plugin-style
     structure.
   * Provide simulator adapters for tests and showcase flows.
   * Provide WooCommerce, fiscal-capture, Econt-compatible, and
     Speedy-compatible shells without requiring live credentials.
   * Ensure each adapter exposes capabilities, validation, execution,
     and error reporting.
   * Ensure adapter failures write integration log entries.
   * Ensure adapter config is environment-driven.

   Done when:

   * adapter interfaces are stable;
   * simulators pass tests;
   * real adapter shells exist without embedded credentials;
   * adapter capability reporting works;
   * adapter failures are logged;
   * docs explain how adapters are configured.

5. [open] Slice 5 - Deliver ERP-to-storefront proof.

   Depends on:

   * Slices 3 and 4

   Surfaces:

   * storefront sync services
   * WooCommerce adapter shell
   * storefront simulator
   * product sync batches
   * stock sync batches
   * availability sync
   * order ingest boundary
   * showcase data
   * storefront docs

   Scope:

   * Create the first visible proof path from ERP truth to storefront
     state.
   * Sync product, price, stock, and availability through a simulator.
   * Keep WooCommerce support credential-free in tests.
   * Ensure incomplete or unsafe products are blocked from sync.
   * Ensure sync success, skip, warning, and failure states are logged.
   * Define the storefront as blind presentation, not source of truth.
   * Provide demo records that prove cause and effect.

   Done when:

   * simulated ERP-to-storefront sync works;
   * sync payloads are testable;
   * unsafe publication is blocked;
   * sync events are logged;
   * order ingest boundary exists;
   * docs explain how the public storefront is connected.

6. [open] Slice 6 - Deliver POS and blackout recovery beta.

   Depends on:

   * Slices 3 and 4

   Surfaces:

   * POS receipt services
   * fiscal capture adapter shell
   * POS simulator
   * replay batches
   * blackout state machine
   * stock mutation guards
   * POS docs

   Scope:

   * Accept POS receipt payloads through a simulator.
   * Represent fiscal receipt references without requiring live
     hardware credentials.
   * Map receipt lines to products where possible.
   * Put unknown products or barcodes into review state.
   * Queue replayable events.
   * Replay safe events.
   * Block unsafe replay.
   * Keep blackout recovery auditable.

   Done when:

   * POS simulator tests pass;
   * safe replay works;
   * unsafe replay is blocked;
   * unknown identities enter review;
   * stock is not silently mutated;
   * blackout docs match runtime behavior.

7. [open] Slice 7 - Deliver courier and COD beta.

   Depends on:

   * Slices 3 and 4

   Surfaces:

   * courier services
   * courier simulator
   * Econt-compatible shell
   * Speedy-compatible shell
   * shipment records
   * courier events
   * COD state
   * return state
   * courier docs

   Scope:

   * Create shipment drafts from ERP order data.
   * Validate shipment payloads before submission.
   * Submit through simulator in tests.
   * Record tracking references.
   * Track COD as pending, confirmed, failed, or reconciled.
   * Track returns and failed delivery states.
   * Ensure courier fee and payout states are visible.
   * Keep real credentials outside the repo.

   Done when:

   * courier simulator tests pass;
   * Econt-compatible and Speedy-compatible shells exist;
   * shipment lifecycle is explicit;
   * COD lifecycle is explicit;
   * returns are explicit;
   * docs explain live credential setup safely.

8. [open] Slice 8 - Deliver accounting and quote-support surfaces.

   Depends on:

   * Slices 3, 5, 6, and 7

   Surfaces:

   * purchasing summaries
   * supplier liability summaries
   * sales summaries
   * COD summaries
   * courier fee summaries
   * export payloads
   * accounting docs
   * sales-demo docs

   Scope:

   * Provide operational accounting summaries.
   * Provide supplier liability views.
   * Provide sales summaries by payment state.
   * Provide COD pending and settled summaries.
   * Provide courier fee summaries.
   * Provide accountant-reviewable export payloads.
   * Provide quote-support talking points based on system data.
   * State clearly that APRP supports operational review and does not
     replace legal accounting judgement.

   Done when:

   * accounting support tests pass;
   * export payloads are deterministic;
   * COD and courier summaries are covered;
   * docs are clear about accounting boundaries;
   * sales-demo material is factual.

9. [open] Slice 9 - Build safe showcase mode.

   Depends on:

   * Slices 3, 5, and 7

   Surfaces:

   * demo data services
   * showcase reset services
   * demo-only markers
   * public demo docs
   * cookie notice
   * screenshare checklist
   * public CTA copy

   Scope:

   * Create safe demo data generation.
   * Create demo reset logic.
   * Mark demo-only records explicitly.
   * Keep demo records separate from production records.
   * Support controlled demo actions where feasible.
   * Avoid unrestricted anonymous ERP access.
   * Add disposable-session language for public demo surfaces.
   * Add a screenshare demo checklist.
   * Add a public quote call-to-action.

   Done when:

   * demo data can be generated;
   * demo data can be reset;
   * demo records are identifiable;
   * public demo boundaries are documented;
   * cookie language exists;
   * screenshare checklist exists;
   * the CTA is present and not overclaimed.

10. [open] Slice 10 - Turn ops into beta-SaaS operations.

    Depends on:

    * Slices 2 through 9

    Surfaces:

    * `ops/opsconfig.yaml`
    * ops config examples
    * deploy scripts
    * backup scripts
    * restore scripts
    * mirror scripts
    * health checks
    * compose files
    * system docs
    * CI

    Scope:

    * Validate config rendering.
    * Validate primary runtime configuration.
    * Validate mirror configuration where Docker is available.
    * Validate deploy script syntax and dry-run behavior where possible.
    * Validate backup script syntax and dry-run behavior where possible.
    * Validate restore script syntax and dry-run behavior where possible.
    * Add a production preflight checklist.
    * Add a restore rehearsal checklist.
    * Add health-check commands.
    * Fix CI environment configuration so repository checks are meaningful.

    Done when:

    * ops tests pass;
    * shell scripts pass syntax checks;
    * compose files validate where Docker is available;
    * CI config is reproducible;
    * backup and restore docs match scripts;
    * mirror status is described honestly;
    * no secrets are committed.

11. [open] Slice 11 - Harden SaaS security boundaries.

    Depends on:

    * Slices 2 through 10

    Surfaces:

    * permissions
    * roles
    * public demo boundaries
    * environment config
    * secret handling
    * CI secret assumptions
    * security docs
    * release checks

    Scope:

    * Verify least-privilege role assumptions.
    * Ensure public demo users cannot reach admin surfaces.
    * Ensure demo actions cannot damage production state.
    * Ensure secrets are not stored in tracked files.
    * Ensure CI does not require production secrets.
    * Ensure live adapter credentials are local or platform-provided.
    * Add security checklist for beta operators.
    * Add release hygiene checks for private data and unwanted identity.

    Done when:

    * security docs match runtime behavior;
    * permission tests exist where feasible;
    * public demo risks are documented;
    * secret handling is explicit;
    * hygiene checks pass;
    * release checklist includes security gates.

12. [open] Slice 12 - Prepare beta-SaaS public release.

    Depends on:

    * Slices 1 through 11

    Surfaces:

    * README
    * SPEC
    * PLAN
    * CHANGELOG
    * docs
    * release docs
    * CI
    * tests
    * public repo metadata

    Scope:

    * Align all public docs with real beta behavior.
    * Keep the stage as beta.
    * Remove alpha wording unless used historically in changelog.
    * Replace production-grade wording with beta-SaaS wording unless a
      claim is proven.
    * Ensure docs do not imply unsupported self-service billing,
      tenant automation, or production support desk workflows.
    * Ensure the public repo description and CTA are aligned.
    * Ensure changelog records the beta-SaaS readiness push.
    * Produce a release candidate summary.

    Done when:

    * public docs are aligned;
    * known limitations are documented;
    * release summary exists;
    * CI status is known;
    * tests pass where dependencies allow;
    * hygiene checks pass;
    * 1.0.0 beta-SaaS readiness can be stated honestly.

## Validation Routine

* Verify tests pass for the active slice.
* Verify Python files compile.
* Verify shell scripts pass syntax checks.
* Verify generated artifacts synchronize after refresh.
* Verify docs and changelog are updated where behavior changed.
* Verify install rehearsals work against smoke-tested config profiles.
* Verify hardcoded hostnames and public URLs do not remain in reusable
  runtime code.
* Verify public endpoints live in config or approved public docs only.
* Verify real secrets, credentials, dumps, keys, and private data are
  absent.
* Verify unwanted previous-business identity is absent.
* Verify simulator tests cover adapter behavior without live credentials.
* Verify public demo behavior cannot expose unrestricted ERP
  administration.
* Verify backup, restore, and mirror assumptions are documented honestly.
* Verify CI configuration is reproducible and does not depend on local
  machine state.
* Verify configured governance checks pass after each slice closes.
* If Docker, ERPNext, Frappe, or live vendor credentials are unavailable,
  record that honestly instead of claiming success.

Minimum validation after a slice:

* run the Python test suite;
* compile Python files;
* check shell script syntax;
* run configured repository checks;
* inspect public docs touched by the slice;
* update `CHANGELOG.md` when behavior changed.

Release validation before 1.0.0 beta-SaaS readiness:

* fresh install path documented;
* core DocTypes validated;
* service tests passing;
* adapter simulator tests passing;
* storefront sync proof passing;
* POS replay tests passing;
* courier/COD tests passing;
* accounting summary tests passing;
* demo data path tested;
* ops scripts syntax-checked;
* compose files validated where possible;
* CI status known;
* security checklist complete;
* public documentation aligned;
* known limitations documented;
* no secrets committed;
* no private data committed;
* no unwanted previous-business identity committed.
