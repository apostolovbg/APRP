# Couriers
**Doc ID:** COURIERS
**Doc Type:** module-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

The APRP courier surface keeps shipping, COD, payout, and return state
explicit.

The courier contract lives in `aprp.aprp.courier_contract`.
It defines courier capability profiles, shipment records, courier events,
and reconciliation summaries so each installation can wire its own carrier
mix without hardcoding brand behavior into the core.
The courier service layer in `aprp.aprp.courier_services` bridges shipment
drafts, tracking references, event logs, dispatch batches, and summaries.

The first courier targets are Speedy and Econt.
The adapter contract is capability-based, so more carriers can be added
without reshaping the product.

The tracked adapter shells are `CourierSimulatorAdapter`,
`CourierSpeedyAdapter`, and `CourierEcontAdapter`.
Live courier API roots and credentials stay in installation config or
secrets, not in the repository.

## Core model

- `Courier Capability` keeps domestic and international delivery, pickup
  modes, COD, label creation, tracking, pickup requests, and returns
  visible.
- `Courier Shipment` keeps the order, courier, service mode, label
  reference, tracking number, COD state, payout state, return state, and
  exception state together.
- `Courier Event` keeps label, handoff, delivery, COD, payout, return, and
  exception updates auditable.
- `Courier Dispatch Batch` groups shipments and events for one courier run.
- `Courier Summary` rolls the courier run into one operator-facing review
  view.

## Workspace and access

Courier surfaces are operator-facing.

Fulfillment staff can create and hand off shipments.
Accounting can review payout, return, and exception summaries.
Public visitors must not see courier administration surfaces.

## Operating rules

- Keep courier selection capability-based rather than brand-hardcoded.
- Keep COD pending until the courier confirms collection and settlement.
- Keep returns and delivery exceptions visible before ERP posting.
- Keep tracking and label references explicit for each shipment.
- Keep courier-specific API roots and credentials in installation config or
  secrets, not in the generic product contract.
