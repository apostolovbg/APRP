# Showcase
**Doc ID:** SHOWCASE
**Doc Type:** operator-guide
**Project Version:** 0.4.0
**DevCovenant Version:** 1.0.1b5

## Overview

APRP safe showcase mode is a controlled public proof surface.
It sits on top of the blind storefront contract and uses demo-only
records, disposable session state, and reset/reseed steps.
The implementation lives in `aprp.aprp.showcase_services`.

Showcase mode is optional. It must never become the ERP authority or mix
with production records.

## Seed and reset

- Use `build_showcase_seed_plan()` to generate demo rows, demo-only
  markers, controlled actions, and the disposable session label.
- Use `build_showcase_reset_plan()` to derive the reset path from the
  seed plan.
- Mark any showcase-only record with `mark_demo_only_record()`.

The tracked seed plan must keep demo-only and production rows separate.
If a demo record overlaps production state, the reset builder must fail.

## Boundary rules

- Public visitors may browse the showcase surface, place sandbox
  actions, and see the safe order flow.
- Anonymous users must not get unrestricted ERP access.
- Session cookies must be disposable and resettable.
- Showcase data must be restorable without touching production rows.
- HTTPS remains mandatory on the public entrypoint.

## Screenshare checklist

1. start from a disposable session;
2. open the seeded storefront rows;
3. show the controlled checkout path;
4. show that the ERP boundary stays hidden;
5. reset the showcase state before ending the session.

## Public demo checklist

1. confirm HTTPS is enabled;
2. confirm anonymous visitors stay on storefront surfaces;
3. confirm demo-only records are marked and separated;
4. confirm the reset path clears the disposable session;
5. confirm production rows are untouched after reset.
