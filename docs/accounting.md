# Accounting
**Doc ID:** ACCOUNTING
**Doc Type:** module-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

The APRP accounting surface turns procurement data into monthly,
reviewable summaries.

The contract lives in `aprp.aprp.purchasing_contract`.
It keeps release forecasts, procurement profiles, purchase liabilities,
cashflow plans, and accounting summaries explicit.

APRP does not replace legal accounting review. It makes operational
accounting data inspectable, repeatable, and ready for period lock
checks.

## Core model

- `Release Forecast` keeps supplier, release, demand, fill rate, and risk
  state explicit.
- `Procurement Profile` groups release forecasts, budget, and salary
  planning for one supplier.
- `Purchase Liability` keeps invoice variance, landed cost, and receipt
  mismatch explicit.
- `Cashflow Plan` keeps opening cash, inflow, outflow, reserve, and
  liquidity gap explicit.
- `Accounting Summary` rolls the same rows into one monthly summary.

## Workspace and access

Accounting surfaces are operator and accountant-facing.

Operators review liabilities, landed cost, and cash pressure.
Accountants review monthly summaries, reserve coverage, and period lock
readiness.
Read-only staff can inspect the summaries when needed.

## Operating rules

- Keep purchase liabilities tied to source invoices and release
  forecasts.
- Keep salary planning and landed cost visible in the same monthly
  review.
- Keep period locking dependent on review-free summaries and reserve
  cash.
- Keep the accounting surface driven from the same operational data as
  purchasing and inventory.
- Treat monthly summaries as operational evidence, not as a substitute
  for accounting judgment.
