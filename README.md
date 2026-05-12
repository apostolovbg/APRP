# APRP
**Doc ID:** README
**Doc Type:** repo-readme
**Project Version:** 0.4.0
**Last Updated:** 2026-05-12
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
6. [Showcase Stack](#showcase-stack)
7. [Documentation](#documentation)
8. [Deployment and Operations](#deployment-and-operations)
9. [Security and Public-Demo Boundaries](#security-and-public-demo-boundaries)
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
- courier, payment, and reconciliation workflows;
- backup, restore, deployment, and continuity discipline;
- clear separation between ERP truth, storefront presentation, and external
  integration surfaces.

APRP is built on the belief that a business should know where its truth lives.

That truth should not live in someone's memory, a spreadsheet tab, and three
broken integrations.

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

The ERP backend and public storefront must remain conceptually separate even
when they are demonstrated together.

## Showcase Stack

The public APRP showcase is planned around:

- `aprp.store` as the public storefront;
- `kuche.aprp.store` as the ERP/showcase backend surface;
- Bulgarian-first storefront assumptions;
- free WordPress/WooCommerce-compatible components where possible;
- Econt and Speedy integration targets;
- ERP-to-storefront synchronization proof;
- disposable demo state for public interaction where feasible.

The showcase goal is not to expose a real production ERP to anonymous users.

The goal is to demonstrate cause and effect:

```text
Change operational state in the ERP/showcase surface
↓
Synchronize through a controlled boundary
↓
Observe the storefront reflect the change
