# APRP
**Doc ID:** README
**Doc Type:** repo-readme
**Project Version:** 0.4.0
**Last Updated:** 2026-05-14
**DevCovenant Version:** 1.0.1b5

<!-- DEVCOV:BEGIN -->

<!-- DEVCOV:END -->

![APRP banner](https://raw.githubusercontent.com/apostolovbg/APRP/main/docs/banner.png)

## Table of Contents

1. [Overview](#overview)
2. [What APRP Is](#what-aprp-is)
3. [What APRP Is Not](#what-aprp-is-not)
4. [Core Principles](#core-principles)
5. [Runtime Model](#runtime-model)
6. [Runtime Stack](#runtime-stack)
7. [Documentation](#documentation)
8. [Deployment and Operations](#deployment-and-operations)
9. [Security and Access Boundaries](#security-and-access-boundaries)
10. [Project Status](#project-status)
11. [Commercial Integration](#commercial-integration)
12. [Maintainer](#maintainer)

## Overview

**APRP** stands for **Advanced Production Resource Planning**.

APRP is ERPNext-based infrastructure for businesses that outgrew spreadsheets,
improvisation, and fragile integrations.

It is an operational framework for inventory-heavy, procurement-aware,
integration-dependent businesses where correctness matters more than cosmetic
dashboards.

APRP exists to turn scattered operational knowledge into explicit, inspectable,
recoverable process.

It focuses on:

- inventory identity and traceability;
- supplier SKU and purchasing structure;
- goods intake and unresolved barcode workflows;
- storefront/POS synchronization patterns;
- courier, COD, returns, and reconciliation workflows;
- backup, restore, deployment, and continuity discipline;
- clear separation between ERP truth, storefront presentation, and external
  integration surfaces.

APRP is built on the belief that a business should know where its truth lives.

That truth should not live in someone's memory, a spreadsheet tab, and three
broken integrations.

All non-secret runtime configuration lives in `ops/opsconfig.yaml`.
The `ops/env.primary.example` and `ops/env.mirror.example` files are for
secrets and machine-local auth only.
The same YAML file also carries the internal service hostnames, ports,
and URLs used by Compose and bootstrap.

## What APRP Is

APRP is a practical foundation for building serious operational systems on top
of ERPNext/Frappe.

It is designed for businesses that need ERPNext to act as the operational
source of truth while storefronts, POS systems, courier tools, payment
systems, and external services remain controlled integration surfaces.

APRP is intended to support implementation patterns such as:

- ERP-owned product identity;
- ERP-owned stock state;
- ERP-owned procurement structure;
- explicit supplier mappings;
- controlled storefront synchronization;
- scanner-friendly warehouse and intake workflows;
- operator review surfaces for unresolved or unsafe data;
- continuity planning before failure happens;
- deploy, backup, restore, and mirror-aware operations.

APRP is not just about adding features.

It is about making operational state explicit enough that a business can stop
depending on folklore, heroics, and manual reconstruction.

## What APRP Is Not

APRP is not a finished SaaS product.

APRP is not a universal one-click ERP.

APRP is not a promise that every business process can be automated without
first understanding it.

APRP is not a dashboard skin.

APRP is not a spreadsheet replacement with nicer buttons.

APRP is a public product, and this repository documents the product contract
directly.

The repository structure, naming, documentation, and boundaries are maintained
as part of that contract.

## Core Principles

### ERP is the operational source of truth

External storefronts and POS systems should not silently become the business
brain.

The ERP must own the state that matters:

- products;
- stock;
- procurement;
- supplier mappings;
- fulfillment state;
- operational exceptions;
- recovery posture.

### Integrations must be disciplined

Integrations are not magic pipes.

They are contracts between systems.

APRP treats integrations as explicit boundaries where data must be mapped,
validated, synchronized, reviewed, and recovered when something fails.

### Inventory must be inspectable

Stock is not just a number.

Stock has identity, movement, source, availability, uncertainty, and
operational history.

APRP prioritizes workflows that make inventory state visible and correctable
instead of hiding ambiguity until it becomes expensive.

### Procurement must be structured

Supplier relationships, supplier SKUs, purchase intent, intake, landed cost,
and availability cannot remain informal forever.

APRP treats procurement as a first-class operational surface, not an
afterthought.

### Recovery is part of the product

Backups, restore paths, deployment procedures, and continuity checks are not
optional extras.

They are part of the operational system.

A system that cannot be restored is not production-ready.

### Business-specific logic must stay isolated

APRP must remain reusable.

Business-specific adapters, workflows, naming, categories, and commercial
assumptions should be isolated from the generic core.

The framework must make specialization possible without contaminating the
foundation.

## Runtime Model

APRP is expected to run as an ERPNext/Frappe custom application with supporting
runtime assets.
It ships its own DocTypes and install hooks as part of the app package.
The runtime service layer in `aprp.aprp.runtime_services` converts contract
data into DocType drafts and validation before Frappe persistence.
The storefront service layer in `aprp.aprp.storefront_services` proves
catalog, stock, availability, batch, and order-ingest flows through the
simulator and WooCommerce shells without real store credentials.
The showcase service layer in `aprp.aprp.showcase_services` proves
demo-only seed, reset, and boundary checks for controlled public
validation without mixing production rows.
The POS service layer in `aprp.aprp.pos_services` proves receipt capture,
line mapping, blackout replay batches, and operator-review state without
live fiscal hardware.
The accounting service layer in `aprp.aprp.accounting_services` proves
purchase summaries, supplier liabilities, sales-state totals, COD
settlement summaries, courier-fee totals, and reviewable export
payloads.

The intended model is:

- ERPNext/Frappe provides the ERP platform;
- APRP provides operational customizations, workflows, integration structure,
  and implementation conventions;
- Docker-based runtime assets provide repeatable deployment and local
  development surfaces;
- WordPress/WooCommerce or another storefront remains separate from the ERP;
- ERP remains the operational source of truth;
- the storefront remains the public sales surface;
- external systems are integrated through controlled adapters and reviewable
  synchronization paths.

The ERP backend and storefront must remain conceptually separate when
they are integrated.

## Runtime Stack

The current APRP baseline is the generalized ERP/ops framework.
The next plan phase builds the product layer on top of it:

- core master data and permissions;
- runtime service helpers for product profiles, intake, and logs;
- POS ingestion helpers and blackout replay proof paths;
- storefront sync helpers and adapter shells for proof paths;
- courier service helpers and adapter shells for proof paths;
- accounting review helpers and export payloads;
- multi-location stock and packaging;
- procurement and cashflow planning;
- blind storefront synchronization;
- POS and Datecs fiscalization;
- courier, COD, and returns workflows;
- config-first installation rehearsal.

Public storefront rollout is a later validation step; the product itself
already includes the blind storefront contract.

## Documentation

Operational guidance lives in `docs/system.md`.
It covers the backend host, the mirror host, site bootstrap, backup,
restore, and recovery sequencing for the APRP runtime.

Inventory modeling lives in `docs/inventory.md`.
Purchasing modeling lives in `docs/purchasing.md`.
POS modeling lives in `docs/pos.md`.
Courier modeling lives in `docs/couriers.md`.
The courier service layer in `aprp.aprp.courier_services` bridges shipment
drafts, tracking references, event logs, dispatch batches, and summaries.
Storefront modeling lives in `docs/storefront.md`.
Showcase modeling lives in `docs/showcase.md`.
Release summary lives in `docs/release.md`.
Installation guidance lives in `docs/install.md`.
Local development guidance lives in `docs/development.md`.
Security and public-demo guidance lives in `docs/security.md`.
Accounting modeling lives in `docs/accounting.md`.
The accounting service layer in `aprp.aprp.accounting_services` bridges
purchase summaries, liability summaries, sales-state totals, COD
settlement summaries, courier-fee summaries, and export payloads.

## Deployment and Operations

APRP is container-first.
The primary ERP runtime is expected on the configured backend host, and the
mirror database member is expected on the configured mirror host.

The repo-owned deploy and backup scripts load `ops/opsconfig.yaml` before they
call Compose or the backup tools.

Non-CI GitHub workflows are generated wrappers around those repo-owned
scripts. They are intended for self-hosted runners or host-managed
checkouts, while `ci.yml` stays DevCovenant-managed.

The current runtime slice uses Galera, ProxySQL, Redis, Caddy, and the APRP
site bootstrap scripts to keep deployment repeatable.

## Security and Access Boundaries

APRP must not commit secrets, private data, or unrestricted admin access.
Public-facing surfaces must remain scoped and reviewable.

## Project Status

APRP is in active alpha.
The repository is the product contract and the runtime implementation target.

## Commercial Integration

APRP is designed to support storefront, courier, POS, and procurement
integrations without letting those systems become the operational authority.
Commercial implementation, onboarding, and integration work are available
for businesses that need a tailored deployment.

## Maintainer

APRP is maintained by its contributors.
