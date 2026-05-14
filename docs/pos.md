# POS
**Doc ID:** POS
**Doc Type:** module-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

The APRP POS surface keeps physical and virtual receipt capture,
fiscalization, and blackout replay explicit.

The contract lives in `aprp.aprp.pos_contract`.
It defines receipt lines, fiscal receipt references, replay batches,
and replay summaries for POS and Datecs-driven sales capture.

The service layer lives in `aprp.aprp.pos_services`.
It turns captured receipts into receipt drafts, replay entries, replay
batches, and operator-review summaries for simulator and Datecs-shaped
proof paths.

POS does not replace ERP inventory authority. It captures sales in a
reviewable form and hands them back into ERP for posting, stock
movement, and accounting.

## Core model

- `Pos Receipt Line` keeps a barcode, quantity, price, and VAT state
  together.
- `Fiscal Receipt Reference` keeps the device and fiscal receipt key
  together.
- `Pos Receipt` keeps the captured receipt, replay state, and fiscal
  reference together.
- `Pos Replay Entry` keeps one queued blackout-replay item explicit.
- `Pos Replay Batch` keeps the receipts, queued entries, and blackout
  state together.
- `Pos Replay Summary` rolls the batch into one operator-facing
  review view.

## Workspace and access

POS surfaces are operator-facing.

Operators and cash-register staff can capture and replay receipts.
Accounting can review the replay summaries and fiscal references.
Public visitors must not see POS administration surfaces.

## Operating rules

- Keep receipt imports idempotent by receipt identity.
- Keep Datecs and other fiscal references explicit and reviewable.
- Keep blackout replay separate from storage, backup, and mirror
  continuity.
- Keep imported receipts replayable when ERP is unreachable.
- Keep receipt mismatches visible before posting into ERP.
- Treat POS capture as a sales surface, not a stock authority.
