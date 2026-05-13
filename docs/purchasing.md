# Purchasing
**Doc ID:** PURCHASING
**Doc Type:** module-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

The APRP purchasing surface keeps supplier, tax, price-list, release,
and accounting review data explicit.

The core contract lives in `aprp.aprp.core_contract`.
The purchasing and accounting contract lives in
`aprp.aprp.purchasing_contract`.
The companion guide in `docs/accounting.md` explains the monthly review
surface that consumes the same data.

Purchasing is the part of the system that explains what must be bought,
who it is being bought from, and how release forecasts turn into
liabilities and cashflow planning.

## Core model

- `APRP Supplier` keeps the supplier identity, VAT ID, and contact data
  together.
- `APRP Tax Profile` keeps VAT defaults and country rules explicit.
- `APRP Price List` keeps the price-list identity and currency together.
- `APRP Product` stays visible so procurement can reference the same item
  identity as inventory.
- `APRP Customer` stays visible as a shared master record for downstream
  operational flows.
- `Release Forecast` keeps supplier VAT ID, release name, demand, fill
  rate, and cash risk explicit.
- `Procurement Profile` groups release forecasts for one supplier and
  budget.
- `Purchase Liability` keeps invoice variance and landed cost explicit.
- `Cashflow Plan` keeps inflow, outflow, reserve, and salary planning
  explicit.
- `Accounting Summary` rolls those rows into a monthly review surface.

## Workspace and access

APRP exposes the purchasing-facing surfaces in the `Purchasing`
workspace.

Operators manage supplier master data, forecasts, liabilities, and
planning. Accounting-facing roles review the monthly summary and period
lock readiness.

## Operating rules

- Keep supplier records structured before purchase intake starts.
- Keep tax profiles explicit instead of burying them in ad hoc notes.
- Keep release forecasts tied to the same product and supplier identity
  used by inventory.
- Keep purchase liabilities and landed cost visible when invoices arrive.
- Keep cashflow planning and salary planning in the same monthly review
  surface.
- Treat purchasing setup as part of the operational core, not a one-off
  import step.
