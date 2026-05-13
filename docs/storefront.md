# Storefront
**Doc ID:** STOREFRONT
**Doc Type:** module-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

The APRP storefront surface keeps the public sales flow blind while
still being real enough to accept and return ERP state.

The contract lives in `aprp.aprp.storefront_contract`.
It defines the catalog rows, order rows, reservations, and sync batch
summary that move between ERP and the storefront.

The storefront is not the ERP authority. ERP still owns product truth,
price truth, stock truth, and reservation truth. The storefront only
exposes the public sales surface and sends customer actions back into
ERP for validation and posting.

## Core model

- `Storefront Catalog Row` keeps ERP-controlled product, price, stock,
  publication, and availability data together.
- `Storefront Order Line` keeps customer-selected quantity and price
  together until ERP reserves it.
- `Storefront Order` keeps the imported checkout state, payment state,
  and HTTPS boundary explicit.
- `Storefront Reservation` keeps the ERP reservation, warehouse, and
  fulfillment state explicit.
- `Storefront Sync Batch` keeps one sync pass and its public safety
  checks together.
- `Storefront Sync Summary` rolls the batch into one operator-facing
  review view.

## Workspace and access

The storefront is public-facing.

Operators control the ERP-to-storefront mapping. Public visitors only
see the storefront surface that ERP approves.
Storefront users must not get direct ERP administration access.

## Operating rules

- Keep product, price, stock, availability, and publication state
  sourced from ERP.
- Keep customer orders flowing back into ERP for reservation and
  accounting.
- Keep public entrypoints on HTTPS.
- Keep public session state temporary and resettable where configured.
- Keep storefront administrators unable to bypass ERP stock authority.
- Treat storefront sync as a controlled boundary, not a business
  source of truth.
