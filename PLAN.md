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

## Overview

APRP must move from an alpha foundation into a working,
production-grade and demo-ready ERPNext-based operational system.

## Mission

APRP must move from an alpha foundation into a working,
production-grade and demo-ready ERPNext-based operational system.

The target is **1.0.0 production-grade and demo-ready completion**.

The runtime model must still support multi-location operations.

For this plan, production-grade and demo-ready completion means:

* the ERPNext app installs cleanly;
* core APRP business objects exist as real Frappe surfaces;
* adapter boundaries exist for storefront, POS, couriers, and accounting;
* at least one ERP-to-storefront proof path works;
* demo data can be created safely;
* deployment, backup, restore, and health-check flows are documented;
* public documentation is honest and sellable;
* no secrets, private data, or legacy identity are present.

APRP is not allowed to remain only contracts and documentation.

The contracts must become runtime behavior.

## Definition of 1.0.0

APRP reaches 1.0.0 when it can support a credible client-facing
production and demo conversation.

1.0.0 requires:

* installable ERPNext/Frappe app package;
* real DocType definitions for the core operational model;
* role and permission fixtures;
* workspace or module navigation;
* validated hooks and app metadata;
* adapter interfaces for storefront, POS, couriers, and accounting;
* at least one working storefront/showcase sync path;
* safe demo data generation;
* safe public showcase assumptions;
* deploy, backup, restore, and health-check scripts;
* tests passing from a clean checkout where local dependencies allow;
* public hygiene checks passing;
* README, SPEC, PLAN, and docs aligned.

1.0.0 does not require:

* paid billing;
* full multi-tenant automation;
* support-desk workflows;
* real courier credentials in the repo;
* real payment credentials in the repo;
* unrestricted anonymous ERP access;
* every possible adapter fully implemented.

1.0.0 must be strong enough that the maintainer can screenshare the ERP,
show the storefront, explain the architecture, and quote full business
integration work.

## Execution Rules

* Work dependency-first.
* Build runtime reality before polishing language.
* Do not mark a slice done unless checks support it.
* Do not treat contract-only code as runtime completion.
* Do not commit real secrets.
* Do not commit real environment files.
* Do not commit database dumps.
* Do not commit private keys.
* Do not commit supplier, customer, or private business data.
* Do not commit legacy project identity.
* Do not expose unrestricted ERP administration to anonymous visitors.
* Prefer a thin working vertical slice over broad unfinished scaffolding.
* Public docs must describe APRP as its own product.
* Keep product identity sharp, but honest.

## Priority Order

If time or tool budget runs out, prioritize:

1. Installable ERPNext/Frappe app.
2. Real DocTypes and fixtures.
3. Storefront/showcase sync proof.
4. Adapter interfaces and simulators.
5. Ops validation and restore confidence.
6. Documentation cleanup.
7. UI polish.

A working thin vertical demo beats a wide unfinished platform.

## Slice 0 — Reality Check

**Status:** open

Inspect the current repository and produce a gap map.

The gap map must state:

* what is already runtime-real;
* what is contract-only;
* what is missing;
* what is unsafe;
* what is overclaimed;
* what must be done first.

Done when:

* the gap map exists in the working summary;
* the next implementation slice is selected;
* no public claims are made beyond current reality.

## Slice 1 — Installable ERPNext App

**Status:** open

Make APRP a real installable ERPNext/Frappe app.

Required surfaces:

* app metadata;
* hooks;
* modules;
* patches file if needed;
* module definition;
* workspace or navigation where useful;
* fixtures where useful;
* install/import validation tests.

Minimum DocType families:

* APRP Product Profile;
* APRP Supplier SKU Mapping;
* APRP Location Policy;
* APRP Intake Session;
* APRP Intake Line;
* APRP Unresolved Barcode;
* APRP Storefront Sync Batch;
* APRP Storefront Sync Event;
* APRP POS Receipt;
* APRP POS Replay Batch;
* APRP Courier Adapter;
* APRP Courier Shipment;
* APRP Courier Event;
* APRP Integration Log.

Done when:

* app imports successfully;
* hooks load successfully;
* required DocType JSON files exist;
* module or workspace structure exists;
* tests cover app surfaces;
* tests pass where dependencies allow.

## Slice 2 — Runtime Services

**Status:** open

Turn contract modules into runtime service helpers.

Required capabilities:

* create or update product profile from APRP contract data;
* validate product publishability;
* create supplier SKU mapping;
* open intake session;
* add intake line;
* detect unresolved barcode;
* post safe intake session;
* block unsafe intake session;
* write integration log entries.

Done when:

* contracts connect to runtime services;
* safe and unsafe paths are tested;
* no service requires live external credentials;
* tests pass.

## Slice 3 — Storefront Sync Proof

**Status:** open

Build the first commercially visible proof path.

Required capabilities:

* generic storefront adapter interface;
* WooCommerce-compatible adapter shell;
* local simulator adapter;
* product sync payload;
* stock sync payload;
* availability sync payload;
* sync batch creation;
* sync event logging;
* order ingest boundary;
* demo product data.

Done when:

* at least one storefront sync path works without real credentials;
* simulated adapter tests pass;
* sync failures are logged;
* unsafe products are blocked from publication;
* docs explain the showcase behavior.

## Slice 4 — POS and Blackout Replay

**Status:** open

Build the POS ingestion and recovery boundary.

Required capabilities:

* generic POS adapter interface;
* fiscal receipt capture boundary;
* simulator adapter;
* receipt validation;
* receipt-line mapping;
* replay batch creation;
* replay state machine;
* unsafe replay blocking;
* operator-review state.

Done when:

* POS receipt tests pass;
* unknown products or barcodes enter review;
* unsafe replay does not silently mutate stock;
* docs explain blackout recovery.

## Slice 5 — Courier Adapter System

**Status:** open

Build courier integration boundaries.

Required capabilities:

* generic courier adapter interface;
* simulator adapter;
* Econt-compatible adapter shell;
* Speedy-compatible adapter shell;
* shipment draft creation;
* shipment validation;
* tracking reference capture;
* COD state tracking;
* return state tracking;
* courier event logging.

Done when:

* courier simulator tests pass;
* adapter shells require no real credentials;
* COD state is explicit;
* return state is explicit;
* docs explain credential configuration without committing secrets.

## Slice 6 — Accounting and Cashflow Support

**Status:** open

Build operational accounting support surfaces.

Required capabilities:

* purchase summary;
* supplier liability summary;
* sales summary by payment state;
* COD settlement summary;
* courier fee summary;
* accountant-reviewable export payload.

Done when:

* accounting support tests pass;
* docs state that APRP supports operational review;
* docs do not claim APRP replaces legal accounting review.

## Slice 7 — Ops Validation

**Status:** open

Harden deployment, backup, restore, mirror, and health-check assumptions.

Required capabilities:

* primary environment example;
* mirror environment example;
* compose validation where Docker is available;
* deploy script syntax validation;
* backup script syntax validation;
* restore script syntax validation;
* health-check documentation;
* production preflight checklist.

Done when:

* ops tests pass;
* scripts pass syntax checks;
* compose files validate where Docker is available;
* docs match actual scripts;
* no secrets are committed.

## Slice 8 — Safe Showcase Mode

**Status:** open

Build the safe demonstration layer.

Required capabilities:

* demo data generation;
* demo reset path;
* demo-only record marking;
* controlled demo actions;
* no unrestricted anonymous ERP access;
* cookie/disposable-session language;
* screenshare demo checklist;
* public demo checklist.

Done when:

* safe demo data can be generated or clearly documented;
* public demo boundaries are explicit;
* demo state cannot mix with production state;
* showcase docs exist;
* tests cover implemented demo safety behavior.

## Slice 9 — Public Documentation

**Status:** open

Align public docs with actual behavior.

Required docs:

* install guide;
* local development guide;
* showcase guide;
* storefront integration guide;
* courier adapter guide;
* POS and blackout guide;
* backup and restore guide;
* security and public-demo guide.

Done when:

* docs match current code;
* alpha status is honest;
* known limitations are explicit;
* commercial integration CTA exists;
* no legacy identity appears;
* public hygiene checks pass.

## Slice 10 — Release Candidate Gate

**Status:** open

Prepare 1.0.0 production-grade and demo-ready release.

Required checks:

* Python tests pass where dependencies allow.
* Python files compile.
* Shell scripts pass syntax checks.
* Compose files validate where Docker is available.
* Tooling checks pass where installed.
* Secret scan passes.
* Private-data scan passes.
* Legacy-identity scan passes.
* Version and changelog are aligned.
* Known limitations are documented.

Done when:

* release summary exists;
* all runnable checks pass;
* blocked checks are documented honestly;
* no secrets are committed;
* no private data is committed;
* no legacy identity remains.

## Validation Routine

For every slice:

* open the appropriate local workflow gate if required;
* make the smallest complete implementation pass;
* add or update tests;
* run relevant tests;
* update docs only to match actual behavior;
* run hygiene checks after copied or generalized material;
* do not claim completion unless validation supports it.

Minimum validation:

* run Python tests;
* compile Python files;
* check shell scripts;
* run configured repository tooling.

Additional validation where available:

* validate Docker Compose files;
* validate mirror Compose files;
* validate adapter simulator tests;
* validate install/import checks.

## Public Hygiene Rules

The repository must contain no:

* real secrets;
* real credentials;
* real environment files;
* database dumps;
* private keys;
* customer data;
* supplier data;
* private business data;
* legacy project identity;
* private implementation history.

Legacy identity checks should be performed using a local or tooling-level
denylist.

The denylist itself should not be published if it contains private or unwanted
terms.

## Release Gate

APRP may be called **1.0.0 production-grade and demo-ready** only when:

* ERPNext app structure is real;
* required DocTypes exist;
* adapter interfaces exist;
* at least one storefront/showcase sync proof works;
* safe demo data exists or is scripted;
* ops scripts are validated as far as possible;
* backup and restore paths are documented;
* public docs are honest;
* tests pass where dependencies allow;
* hygiene checks pass;
* no secrets are committed;
* no private data is committed;
* no legacy identity remains.

The 1.0.0 release should support this sales sentence:

> APRP is an ERPNext-based operational framework for businesses that outgrew
> spreadsheets, improvisation, and fragile integrations. The showcase
> demonstrates ERP-owned inventory, procurement, storefront/POS, courier, and
> continuity patterns. Full business integration is quoted separately.
