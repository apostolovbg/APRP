# Inventory
**Doc ID:** INVENTORY
**Doc Type:** module-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

The APRP inventory surface turns the core business contract into an
operational stock model.

The core contract lives in `aprp.aprp.core_contract`.
The inventory contract lives in `aprp.aprp.inventory_contract`.

`aprp.aprp.core_contract` defines the product, location, supplier,
customer, tax, and price-list records that stock work depends on.

`aprp.aprp.inventory_contract` defines the pack-family, warehouse-policy,
intake-session, unresolved-barcode, stock-operation, and safety-gate
records that move stock through the system.

Inventory is not a sidecar checklist. It is the part of the system that
explains what exists, where it exists, and which location can move it.

## Core model

- `APRP Product` keeps stable identity, barcode, supplier, tax, and
  price-list references together.
- `APRP Location` binds a location name to a warehouse and company.
- `APRP Warehouse Policy` defines the location-to-warehouse purpose split.
- `APRP Customer` stays as shared master data for downstream sales and
  support work.
- `Pack Family` keeps unit, box, and case tiers explicit.
- `Intake Session` keeps barcode-first intake staged before posting.
- `Unresolved Barcode` keeps unknown scans visible until mapped.
- `Inventory Safety Gate` blocks publishing and selling when stock truth is
  missing or inconsistent.

## Workspace and access

APRP exposes the inventory-facing surfaces in the `Inventory` workspace.

Operator and staff roles can manage inventory data. Location-scoped users can
read the relevant master data and submit location events without gaining
global authority.

## Operating rules

- Keep stock policy explicit for each physical location.
- Keep fulfillment, reserve, and intake warehouses separate by purpose.
- Keep sealed pack tiers explicit at unit, box, and case levels.
- Keep barcode-first intake staged and reviewable before posting.
- Keep reservations explicit before stock is exposed for sale.
- Keep customer records separate from ad hoc notes or spreadsheet-only data.
- Treat the inventory workspace as the navigation entrypoint for stock truth.
- Do not let storefronts or couriers become the stock authority.
