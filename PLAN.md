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
- APRP is a config-driven ERPNext operational system for Bulgarian
  commerce and inventory-heavy businesses.
- The runtime baseline already passes smoke tests; this plan covers the
  next phase of product implementation on top of that baseline.
- Public publication and showcase work are later validation steps, not
  the product definition.
- The product must support one blind WooCommerce storefront, multiple
  physical locations, packaging relations, POS and Datecs fiscalization,
  couriers, COD, and recoverable operations.
- Non-secret runtime config stays in `ops/opsconfig.yaml`; hardcoded
  hostnames and public URLs do not belong in non-config artifacts.
- Repo-owned scripts remain the contract for deploy, backup, mirror,
  and installation rehearsal.
- The product target is a real ERP system that a tech-savvy operator
  can install, configure, and run.

## How Slices Are Executed
- Each slice means a complete end-to-end implementation pass, not a
  partial triage note.
- Keep the scope of one slice inside the files named in that slice.
- Update the slice status in the same session when work lands.
- Do not start later slices before earlier dependency slices are
  complete.
- Concrete installation settings belong in tracked `ops/` config, not
  hardcoded in reusable runtime code or docs.
- The repo-owned scripts translate `ops/opsconfig.yaml` into the shell
  environment before runtime, deploy, backup, or recovery run.
- Public hostnames, mirror members, and other environment-specific
  addresses belong in tracked config or local instance files, not in
  compose files or other non-config artifacts.
- Repo-owned scripts are the source of truth for deploy, backup, mirror
  bootstrap, and install-time orchestration.
- Use `CHANGELOG.md` to record the slice outcome when behavior or
  governance changes.
- Use `devcovenant gate --open`, `devcovenant gate --verify`,
  `devcovenant run`, and `devcovenant gate --close` around each
  completed slice.

## Execution Slices
1. [done] Slice 1 - Model the ERP business core.
   Depends on:
   - runtime baseline
   Surfaces:
   - app doctypes and permissions
   - workspace and module config
   - aprp/aprp/core_contract.py
   - docs/inventory.md
   - docs/purchasing.md
   Scope:
   - Define stable product, supplier, customer, location, warehouse,
     tax, and price-list models.
   - Keep ERPNext-native module and workspace navigation explicit.
   - Give the system permission domains for operators, staff, and
     location-scoped users.
   Done when:
   - core business objects exist and are explicit in the app;
   - product identity and operator permissions are represented cleanly;
   - the system can describe one business with multiple locations.
   Implemented:
   - aprp/aprp/core_contract.py
   - docs/inventory.md
   - docs/purchasing.md
   - tests/test_aprp_core_contract.py
2. [done] Slice 2 - Build inventory, packaging, and location policy.
   Depends on:
   - Slice 1
   Surfaces:
   - stock doctypes
   - packaging logic
   - warehouse policy
   - aprp/aprp/inventory_contract.py
   - docs/inventory.md
   Scope:
   - Implement per-location warehouses and explicit fulfillment,
     reserve, and intake policy.
   - Keep sealed and open pack state explicit at unit, box, and case
     levels.
   - Support barcode-first intake, stock moves, transfers, counts, and
     reservations.
   - Block unsafe publishing or selling when stock data is missing or
     inconsistent.
   Done when:
   - multi-location stock is explicit;
   - pack families and reservations are first-class;
   - per-location policy drives fulfillment and intake.
   Implemented:
   - aprp/aprp/inventory_contract.py
   - docs/inventory.md
   - tests/test_aprp_inventory_contract.py
3. [done] Slice 3 - Add procurement, release forecasting, and cashflow
   hooks.
   Depends on:
   - Slices 1 and 2
   Surfaces:
   - procurement doctypes
   - accounting hooks
   - aprp/aprp/purchasing_contract.py
   - docs/purchasing.md
   - docs/accounting.md
   - tests/test_aprp_purchasing_contract.py
   Scope:
   - Turn supplier feeds and release signals into procurement profiles.
   - Carry supplier liabilities, landed cost, and salary planning into
     ERP-facing accounting surfaces.
   - Keep release forecasting as an input to procurement, not the whole
     system.
   - Make accountant-ready outputs possible from the same source data.
   Done when:
   - procurement informs stock planning and cashflow;
   - liabilities and release risk are explicit;
   - the accounting surfaces can consume the same operational data.
   Implemented:
   - aprp/aprp/purchasing_contract.py
   - docs/accounting.md
   - docs/purchasing.md
   - tests/test_aprp_purchasing_contract.py
4. [done] Slice 4 - Synchronize the blind storefront and order flow.
   Depends on:
   - Slices 1, 2, and 3
   Surfaces:
   - storefront integration
   - order sync
   - aprp/aprp/storefront_contract.py
   - docs/storefront.md
   - tests/test_aprp_storefront_contract.py
   Scope:
   - Keep the storefront as a sales surface only.
   - Sync product, price, stock, availability, and publication state
     from ERP.
   - Move customer orders back into ERP for reservation, fulfillment,
     and accounting.
   - Preserve Bulgarian-first storefront behavior and HTTPS.
   - Keep the storefront unable to mutate authoritative stock or
     product truth.
   Done when:
   - the storefront reads from ERP truth;
   - orders and reservations flow back to ERP;
   - storefront administrators cannot bypass ERP authority.
   Implemented:
   - aprp/aprp/storefront_contract.py
   - docs/storefront.md
   - tests/test_aprp_storefront_contract.py
5. [done] Slice 5 - Capture POS, fiscalization, and blackout
   recovery.
   Depends on:
   - Slices 1, 2, 3, and 4
   Surfaces:
   - POS adapters
   - Datecs integration
   - offline recovery
   - aprp/aprp/pos_contract.py
   - docs/pos.md
   - tests/test_aprp_pos_contract.py
   Scope:
   - Support Datecs fiscalization and POS capture paths.
   - Keep offline sales replayable when ERP is unreachable.
   - Make blackout mode bounded, auditable, and recoverable.
   - Reconcile fiscal receipts, sales, and stock movement in ERP.
   Done when:
   - physical and virtual POS capture land in ERP;
   - offline receipts can be replayed;
   - blackout recovery is documented and exercised.
   Implemented:
   - aprp/aprp/pos_contract.py
   - docs/pos.md
   - tests/test_aprp_pos_contract.py
6. [done] Slice 6 - Wire couriers, COD, returns, and installation
   rehearsal.
   Depends on:
   - Slices 1, 2, 3, 4, and 5
   Surfaces:
   - aprp/aprp/courier_contract.py
   - courier adapters
   - shipping rules
   - install validation
   - docs/couriers.md
   - docs/system.md
   Work to do:
   - Model Speedy and Econt integrations as adapters.
   - Keep COD pending until courier confirmation.
   - Track shipment, payout, return, and fee state explicitly.
   - Prove a fresh install works from `ops/opsconfig.yaml` plus
     secrets.
   - Run deploy, backup, restore, and mirror drills against the product
     model.
   - Treat any future public-facing showcase work as a separate plan.
   Done when:
   - courier events update ERP truth;
   - COD and returns stay auditable;
   - a concrete install can be rehearsed end-to-end from config-only
     setup.
   Implemented:
   - aprp/aprp/courier_contract.py
   - docs/couriers.md
   - docs/system.md
   - tests/test_aprp_courier_contract.py

## Validation Routine
- Verify tests pass for the active slice.
- Verify generated artifacts synchronize after refresh.
- Verify documentation and changelog are updated where behavior changed.
- Verify install rehearsals work against smoke-tested config profiles.
- Verify hardcoded hostnames and public URLs do not remain in compose
  files or other non-config artifacts.
- Verify `devcovenant check` passes after the slice closes.
