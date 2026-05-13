# Project Specification
**Doc ID:** SPEC
**Doc Type:** specification
**Project Version:** 0.4.0
**Project Stage:** beta
**Maintenance Stance:** active
**Compatibility Policy:** forward-only
**Versioning Mode:** versioned
**Last Updated:** 2026-05-13
**DevCovenant Version:** 1.0.1b5

<!-- DEVCOV:BEGIN -->
This opening section is managed by DevCovenant.
Use `SPEC.md` only for durable project rules below this block.
<!-- DEVCOV:END -->

## Overview

This specification defines the durable product, ERP, storefront,
integration, infrastructure, security, and operational rules for **APRP**.

**APRP** stands for **Advanced Production Resource Planning**.

APRP is ERPNext-based infrastructure for businesses that outgrew
spreadsheets, improvisation, and fragile integrations.

APRP's HTTPS, storefront integration, deploy, backup, and mirror
recovery capabilities are first-class product targets.

## Ops Configuration

APRP framework behavior stays address-agnostic.

All non-secret installation settings live in `ops/opsconfig.yaml`.
The repo-owned scripts translate that YAML file into the shell
environment they need for Compose, deploy, backup, and recovery.
That YAML file carries the internal service hostnames, ports, and URLs
used by the runtime stack.

The installation-specific config shape is tracked in
`ops/opsconfig.yaml.example`.

Operators copy that file to an untracked `ops/opsconfig.yaml` instance
file and edit the same keys for the installation.

The tracked example and the local instance file share the same keys and
sections.

Any installation that matches that tracked shape must be smoke-testable.

Hardcoded hostnames and public URLs do not belong in compose files or
other non-config artifacts.

Untracked environment files remain reserved for secrets and
machine-local auth only.

In this specification:

* **ERP** means the ERPNext/Frappe system running APRP.
* **Storefront** means the public WordPress/WooCommerce sales surface.
* **Operator** means an authenticated person performing ERP-side work.

APRP is not a dashboard skin.

APRP is not a spreadsheet with nicer buttons.

APRP is the operational layer where product truth, inventory truth,
procurement truth, integration truth, and recovery truth must live.

## 0. Status

* This file is the single source of truth for durable APRP behavior.
* This file is not a roadmap.
* This file does not describe migration history.
* This file does not describe temporary implementation steps.
* APRP behavior is generalized and config-driven.
* All non-secret configuration lives in `ops/opsconfig.yaml`.
* Any installation that matches the tracked config shape must be
  smoke-testable.
* Decisions are locked by default.
* Changes to locked behavior require explicit maintainer approval.
* Public-facing behavior must never weaken production security
  assumptions.

## 1. Product Profile, Goals, and Principles

### 1.1 Product profile

* Product name: APRP.
* Full name: Advanced Production Resource Planning.
* Product type: ERPNext-based operational framework.
* Primary platform: ERPNext/Frappe.
* Primary language posture: Bulgarian-first.
* Secondary language posture: English-compatible.
* Primary target users:

  * small and medium businesses;
  * inventory-heavy businesses;
  * procurement-aware businesses;
  * businesses with storefront/POS/courier integrations;
  * businesses that need recoverable operational infrastructure.
* Initial storefront stack:

  * WordPress;
  * WooCommerce;
  * free or low-cost themes/plugins where feasible;
  * Econt and Speedy integration targets.
* Timezone baseline: Europe/Sofia.
* Currency baseline:

  * BGN for Bulgarian storefront behavior;
  * EUR-compatible accounting and reporting where required.

### 1.2 Product goals

APRP must provide a reusable ERPNext-based framework for:

* product and inventory control;
* supplier and procurement structure;
* barcode-aware stock intake;
* unresolved barcode handling;
* storefront synchronization;
* POS and offline-sales ingestion patterns;
* courier and COD workflow modelling;
* backup, restore, deploy, and continuity discipline;
* storefront integration without exposing real administration.

APRP must help a business answer:

* what exists;
* where it exists;
* what can be sold;
* what must be purchased;
* what has been received;
* what is uncertain;
* what was synchronized;
* what failed;
* what can be recovered.

### 1.3 Technical principles

* ERPNext/Frappe is the ERP foundation.
* APRP custom logic lives in an ERPNext/Frappe custom app.
* ERP is the operational source of truth.
* Storefronts are public sales surfaces, not the business brain.
* POS systems are sales capture surfaces, not the inventory authority.
* Couriers are fulfillment/payment partners, not accounting truth.
* Integrations must be explicit, reviewable, and recoverable.
* Data integrity is preferred over convenience.
* Missing required operational fields must block unsafe publishing or selling.
* Business-specific behavior must stay isolated from the generic framework.
* Deployment and recovery are part of the product.
* A system that cannot be restored is not production-ready.
* Runtime wiring must come from tracked config and local secrets, not
  hardcoded host assumptions.
* HTTPS, storefront routing, deploy, backup, and mirror recovery are
  first-class APRP targets.
* Public web entrypoints must use HTTPS with secure cookies and HSTS.

## 2. Authority Boundaries

### 2.1 ERP authority

ERP owns:

* product identity;
* internal item IDs;
* barcode/EAN/GTIN mappings;
* supplier SKU mappings;
* stock state;
* warehouses and stock locations;
* procurement records;
* purchase intake;
* fulfillment state;
* operational exceptions;
* integration logs;
* recovery posture.

### 2.2 Storefront authority

The storefront owns:

* public presentation;
* public product pages;
* shopping cart UX;
* checkout UX;
* customer-facing content;
* marketing pages;
* storefront theme behavior.

The storefront must not silently become the authority for:

* stock truth;
* procurement truth;
* internal product identity;
* warehouse state;
* supplier mappings;
* ERP-side accounting records.

### 2.3 POS authority

POS systems may capture:

* fiscal sales;
* in-store payments;
* receipt references;
* offline sales events;
* payment-method metadata.

POS systems must not become the primary source of inventory truth.

### 2.4 Courier authority

Courier systems may provide:

* shipment labels;
* tracking numbers;
* COD state;
* delivery state;
* returned shipment state;
* fee and payout information.

Courier systems must not become the primary source of order truth.

## 3. High-Level Architecture

### 3.1 Components

The APRP system consists of:

* ERPNext/Frappe runtime;
* APRP custom app;
* MariaDB database;
* Redis services required by Frappe;
* background workers and scheduler;
* Docker/Compose runtime assets;
* WordPress/WooCommerce storefront;
* courier integration adapters;
* POS ingestion adapters;
* backup and restore scripts;
* deployment scripts;
* storefront integration layer.

### 3.2 Runtime surfaces

Required runtime surfaces:

```text
configured-storefront-host
configured-backend-host
configured-mirror-host
```

`configured-storefront-host` is the storefront surface when the
installation enables one.

`configured-backend-host` is the ERP surface.

`configured-mirror-host` is the mirror database member.

These surfaces are first-class targets and must be driven by config,
not hardcoded addresses in compose files or other non-config artifacts.

### 3.3 Repository path contract

The default host checkout path is:

```text
/opt/aprp/APRP
```

Docker, deploy, backup, mirror, and operator scripts should assume this path
unless explicitly configured otherwise.

### 3.4 Container posture

APRP is container-first.

Local, staging, and production-like deployments should use the same
containerized assumptions where feasible.

The system must avoid hidden machine-specific setup that cannot be documented,
replayed, or inspected.

Compose files and other non-config artifacts must not hardcode
deployment hostnames, mirror members, or public URLs.

## 4. Core Modules

### 4.1 Catalog

The catalog module covers:

* item identity;
* public item eligibility;
* internal SKU;
* barcode/EAN/GTIN;
* supplier SKU mapping;
* item grouping;
* item attributes;
* pack or bundle relationships;
* image state;
* storefront publication state.

A sellable item must have sufficient identity to be scanned, stocked,
synchronized, and audited.

### 4.2 Inventory

The inventory module covers:

* stock quantity;
* stock location;
* warehouse policy;
* intake sessions;
* stock moves;
* corrections;
* reservations;
* unresolved barcode records;
* stock visibility rules;
* blocked/unsafe stock state.

Stock is not only a number.

Stock has source, location, uncertainty, movement, and operational history.

### 4.3 Purchasing

The purchasing module covers:

* suppliers;
* supplier SKUs;
* purchase orders;
* purchase invoices;
* expected quantities;
* received quantities;
* unit costs;
* landed costs;
* charges;
* procurement notes;
* supplier reliability metadata.

Procurement must be structured enough that the business can see what was
ordered, what arrived, what is missing, and what changed.

### 4.4 Sales

The sales module covers:

* storefront orders;
* ERP sales orders;
* invoices;
* reservations;
* payment state;
* fulfillment state;
* cancellation;
* returns;
* stock release;
* manual correction.

Sales must not reduce stock invisibly.

Sales must either reserve, consume, or explicitly fail against ERP-visible
stock state.

### 4.5 POS ingestion

The POS ingestion module covers:

* receipt import;
* offline sales capture;
* fiscal receipt references;
* payment-method metadata;
* blackout recovery;
* replay queue;
* operator review.

POS ingestion must support recovery from periods where the storefront or ERP
was unavailable, while preserving auditability.

### 4.6 Couriers

The courier module covers:

* shipping method mapping;
* courier order creation;
* label references;
* tracking;
* COD state;
* courier payout state;
* returns;
* delivery exceptions.

Initial courier targets:

* Econt;
* Speedy.

Courier adapters must isolate courier-specific behavior from the generic APRP
core.

### 4.7 Accounting support

APRP provides operational accounting support, not a replacement for legal
accounting review.

Minimum accounting support includes:

* purchase totals;
* sales totals;
* payment state;
* COD state;
* courier payout state;
* VAT-relevant exports where configured;
* adjustment records;
* monthly review surfaces.

### 4.8 Storefront integration

The storefront module covers APRP behavior without exposing
unrestricted ERP access.

The storefront must support:

* visible ERP-to-storefront cause and effect;
* safe public browsing and checkout behavior;
* temporary visitor state where feasible;
* resettable public session state where configured;
* safe actions only;
* clear cookie/session disclosure;
* HTTPS-only public entrypoints;
* no real account creation for visitors;
* no production secrets;
* no real supplier/customer data.

## 5. Data Model

### 5.1 Item

An Item represents a product, component, service, pack, bundle, or other
sellable or stock-relevant entity.

Required fields for sellable stock items:

* internal item ID;
* item name;
* item group;
* barcode/EAN/GTIN or explicit barcode-exempt reason;
* stock unit;
* sales unit;
* publication eligibility state;
* stock tracking policy.

Optional fields:

* supplier SKU mappings;
* images;
* storefront title;
* storefront description;
* dimensions;
* weight;
* tax class;
* shipping class;
* pack relation;
* bundle relation.

### 5.2 Supplier

A Supplier represents a vendor, distributor, producer, importer, or other
purchase source.

Required fields:

* supplier name;
* supplier type;
* country;
* active/inactive state.

Optional fields:

* VAT number;
* contact email;
* contact phone;
* default currency;
* lead time;
* ordering notes;
* supplier SKU policy.

### 5.3 Supplier SKU Mapping

A Supplier SKU Mapping links a supplier-specific identifier to an APRP item.

Required fields:

* supplier;
* supplier SKU;
* APRP item;
* purchase unit;
* active/inactive state.

Optional fields:

* minimum order quantity;
* case size;
* last known cost;
* supplier description;
* supplier barcode;
* confidence state.

### 5.4 Warehouse

A Warehouse represents a stock-holding location.

Required fields:

* warehouse name;
* location type;
* active/inactive state.

Location types may include:

* main warehouse;
* storefront/showroom;
* reserve;
* damaged;
* returned;
* quarantine;
* display.

### 5.5 Stock Intake Session

A Stock Intake Session represents a controlled receiving event.

Required fields:

* session ID;
* supplier or source;
* operator;
* start timestamp;
* state.

States:

* draft;
* scanning;
* review;
* posted;
* cancelled.

A posted intake session must create ERP-visible stock movement or correction.

### 5.6 Stock Intake Line

A Stock Intake Line represents one received product or unresolved scan inside
an intake session.

Required fields:

* intake session;
* scanned code or selected item;
* quantity;
* resolution state.

Resolution states:

* resolved;
* unresolved barcode;
* quantity mismatch;
* blocked;
* posted.

### 5.7 Unresolved Barcode

An Unresolved Barcode record captures scanned identity that cannot yet be
mapped safely.

Required fields:

* scanned code;
* first seen timestamp;
* source workflow;
* resolution state.

Resolution states:

* open;
* mapped;
* ignored;
* duplicate;
* blocked.

Unresolved barcode records must not silently create sellable stock.

### 5.8 Sales Order

A Sales Order represents customer purchase intent.

Required fields:

* order source;
* customer or guest reference;
* order lines;
* payment state;
* fulfillment state;
* stock reservation state.

Payment states:

* unpaid;
* paid;
* COD;
* refunded;
* partially refunded;
* failed.

Fulfillment states:

* pending;
* reserved;
* picking;
* shipped;
* delivered;
* returned;
* cancelled.

### 5.9 Courier Shipment

A Courier Shipment represents a shipment request or shipment record.

Required fields:

* courier;
* related sales order;
* recipient data;
* shipment state.

Shipment states:

* draft;
* requested;
* label_created;
* handed_over;
* in_transit;
* delivered;
* returned;
* failed;
* cancelled.

### 5.10 Integration Log

An Integration Log records cross-system synchronization.

Required fields:

* integration name;
* direction;
* entity type;
* entity reference;
* timestamp;
* result state.

Result states:

* success;
* skipped;
* warning;
* failed;
* queued;
* replayed.

Integration errors must be visible to operators.

## 6. Inventory Rules

### 6.1 Barcode rules

* Barcode-first operation is preferred.
* Sellable stocked items should have barcode/EAN/GTIN identity.
* Items without barcodes must carry an explicit exemption reason.
* Unknown scans create unresolved barcode records.
* Unknown scans must not silently create sellable stock.

### 6.2 Stock intake rules

* Stock intake must be session-based.
* Operators must be able to scan, review, resolve, and post.
* Posting must be explicit.
* Mismatches must be visible.
* Cancelled sessions must not affect stock.
* Posted sessions must be auditable.

### 6.3 Stock reservation rules

* Storefront orders should reserve ERP stock before final fulfillment.
* Stock reservation must be visible in ERP.
* Cancelled orders must release reserved stock.
* Returned goods must not become sellable until accepted by policy.

### 6.4 Unsafe stock rules

Stock may be blocked when:

* barcode is unresolved;
* item identity is ambiguous;
* supplier mapping is untrusted;
* returned item requires inspection;
* quantity mismatch requires review;
* integration failure creates uncertainty.

Blocked stock must not be published as sellable stock.

## 7. Purchasing Rules

### 7.1 Supplier identity

Suppliers must be represented explicitly.

Supplier-specific identifiers must not replace APRP item identity.

### 7.2 Purchase import

Purchase import must preserve:

* supplier;
* supplier document reference;
* supplier SKU;
* quantity;
* unit cost;
* charges where available;
* currency;
* date;
* operator review state.

### 7.3 Cost tracking

APRP must preserve enough purchase-cost information to support:

* stock valuation review;
* margin review;
* landed-cost review;
* supplier comparison;
* accounting export.

### 7.4 Procurement visibility

Operators must be able to see:

* what was ordered;
* what arrived;
* what is missing;
* what is blocked;
* what requires mapping;
* what requires supplier follow-up.

## 8. Storefront Integration

### 8.1 Storefront role

The storefront is a public sales surface.

The storefront must receive product, price, stock, and availability state from
ERP-controlled workflows.

Humans should not use the storefront as the primary product-management system
when ERP authority exists.

### 8.2 ERP to storefront

ERP-to-storefront synchronization may include:

* product creation;
* product updates;
* stock updates;
* price updates;
* category mapping;
* image mapping;
* availability state;
* shipping class;
* tax class.

ERP must not publish unsafe or incomplete items.

### 8.3 Storefront to ERP

Storefront-to-ERP synchronization may include:

* orders;
* customers;
* payment status;
* shipping selections;
* cancellation events;
* refund events.

Storefront data entering ERP must be validated and logged.

### 8.4 Bulgarian-first storefront

The public storefront must support Bulgarian-first operation.

English support may be added where feasible, but Bulgarian storefront behavior
is the baseline for the storefront.

### 8.5 Free-stack constraint

The initial storefront should prefer free or low-cost WordPress and
WooCommerce-compatible components.

Paid plugins may be supported later but must not be required for the initial
storefront unless explicitly approved.

## 9. POS and Blackout Recovery

### 9.1 POS ingestion

APRP must support POS ingestion patterns for offline or in-store sales.

POS ingestion must capture:

* receipt reference;
* timestamp;
* payment method;
* sold items;
* quantities;
* totals;
* operator review state.

### 9.2 Blackout recovery

A blackout is a period where ERP, storefront, POS, courier, or integration
connectivity is unavailable or unreliable.

APRP must support replay or review of sales captured during blackout periods.

Blackout recovery must prefer correctness over silent automation.

### 9.3 Replay queue

Replayable events must have:

* source;
* timestamp;
* payload;
* target entity;
* replay state;
* error state;
* operator notes.

Replay states:

* queued;
* replayed;
* skipped;
* failed;
* requires_review.

## 10. Courier and COD Rules

### 10.1 Couriers in scope

Initial courier targets:

* Econt;
* Speedy.

Other couriers may be added through adapters.

### 10.2 COD lifecycle

COD orders must track:

* order creation;
* shipment creation;
* courier handoff;
* delivery;
* COD collection;
* courier payout;
* return or failure.

COD collection must not be treated as settled revenue until the payout state is
known or reconciled.

### 10.3 Shipping methods

Shipping methods must be mapped explicitly between ERP, storefront, and
courier.

Ambiguous shipping methods must require operator review.

### 10.4 Courier exceptions

Courier exceptions must be visible.

Examples:

* failed label creation;
* invalid address;
* failed delivery;
* returned shipment;
* COD mismatch;
* payout mismatch.

## 11. Storefront and Entrypoint Rules

### 11.1 Storefront boundary

The storefront exists to present APRP-controlled product and order
state.

It must not expose unrestricted ERP administration.

Any public entrypoints must be driven by config and kept separate from
operator surfaces.

### 11.2 Session and state safety

Public-facing session state, when configured, must be temporary,
resettable, and clearable without affecting ERP truth.

Public-facing actions must not depend on real business data unless the
installation explicitly enables that behavior for controlled testing.

### 11.3 Transport security

The storefront and any other public entrypoints must be HTTPS-only.

HTTP requests must redirect to HTTPS.

Cookies for public-facing sessions must be secure and protected.

HSTS must be enabled for public entrypoints.

## 12. Security Rules

### 12.1 Secrets

The repository must not contain:

* real `.env` files;
* API keys;
* courier credentials;
* payment credentials;
* database dumps;
* private keys;
* access tokens;
* customer exports;
* supplier invoices;
* private commercial documents;
* production host secrets.

Only templates, examples, and fake example values may be committed.

### 12.2 Access control

Production administration must require authenticated operator access.

Any public-facing storefront access must remain scoped to the surfaces
explicitly configured for that installation.

Anonymous users must never reach unrestricted ERP administration.

Role and permission rules must prefer least privilege.

### 12.3 Public-facing blast radius

Public-facing functionality must be designed so that abuse cannot damage:

* production ERP state;
* production storefront state;
* server configuration;
* secrets;
* backups;
* deploy keys;
* operator accounts.

### 12.4 Auditability

Important actions must be logged.

Integration failures, stock corrections, purchase intake, and public-
facing mutations must leave enough trace to diagnose behavior.

## 13. Continuity, Backup, and Restore

### 13.1 Continuity principle

Recovery is part of APRP.

Git and deploy scripts are not substitutes for durable ERP state.

Durable ERP state includes:

* MariaDB rows;
* uploaded files;
* site configuration;
* private files;
* integration state;
* operational logs.

### 13.2 Backup

The backup system must capture:

* database state;
* site files;
* private files where applicable;
* configuration copies where safe;
* metadata;
* timestamped session identity.

Backups must support local and offsite storage.

A backup that cannot be found, verified, or restored is not sufficient.

### 13.3 Restore

Operators must be able to restore APRP to a non-production target using
documented steps.

Restore documentation must cover:

* database restore;
* file restore;
* site configuration;
* post-restore checks;
* application migration;
* scheduler/worker recovery;
* storefront reconnection where applicable.

### 13.4 Mirror posture

APRP may support a database mirror for reduced data-loss risk.

The baseline mirror model is:

* MariaDB-compatible database layer;
* containerized services;
* single-writer routing;
* split-brain refusal;
* documented rebuild path;
* health checks;
* operator-visible state.

The same contract must support additional mirror members from config
without changing the product rules.

The framework must accept additional members from config.

A mirror does not replace backups.

Backups and mirrors solve different failure modes.

### 13.5 Health checks

Health checks must cover:

* ERP web response;
* worker/scheduler state;
* database state;
* Redis state;
* integration queues;
* backup freshness;
* storefront reachability where applicable.

## 14. Deployment Rules

### 14.1 Deploy contract

Deployment must update code and schema on an existing site.

Deployment must not silently replace live data from backup.

Deployment must leave an operator-visible result.

### 14.2 Environment

Runtime configuration must come from environment files, host secrets, or
approved secret stores.

Non-secret runtime configuration must come from `ops/opsconfig.yaml`.

Tracked examples may exist.

Tracked live secrets must not exist.

GitHub-hosted secrets may be used only for optional remote orchestration;
local installs must remain usable with host-managed config and secrets.

### 14.3 Post-deploy checks

Post-deploy checks should include:

* site availability;
* migration success;
* worker state;
* scheduler state;
* integration health;
* backup trigger or backup freshness check;
* error-log review.

### 14.4 Automation wrappers

`ci.yml` remains DevCovenant-managed.

Any non-CI GitHub workflows must be generated wrappers around repo-owned
scripts.

Deploy, backup, and mirror bootstrap logic must live in repo-owned scripts so
the wrappers cannot drift.

Operational secrets should live on the deployment host or a self-hosted
runner when orchestration needs them; GitHub is not the default secret
store for APRP operations.

## 15. Testing and Validation

### 15.1 Test posture

Tests must be runnable from a clean checkout with documented setup.

Test behavior should cover:

* app import;
* DocType integrity;
* stock workflow rules;
* purchasing workflow rules;
* storefront sync logic;
* POS ingestion logic;
* courier adapter boundaries;
* backup/restore script syntax;
* generalized config and secret smoke tests;
* public-facing safety boundaries.

### 15.2 Validation before public-facing rollout

Before public-facing rollout, APRP must validate:

* no real secrets are committed;
* no private data is committed;
* public visitors cannot access admin surfaces;
* HTTPS is enforced on public entrypoints;
* the generalized install passes smoke tests against the tracked config
  shape;
* any public-facing installation profile passes only after the
  generalized install smoke tests succeed;
* storefront sync proof works;
* backup and restore documentation exists.

## 16. Documentation Rules

Required documentation:

* `README.md` for product identity and entry point;
* `SPEC.md` for durable product rules;
* `BUSINESS.md` for target business assumptions;
* `PLAN.md` for execution slices when needed;
* `docs/system.md` for infrastructure and operations;
* `docs/inventory.md` for stock workflows;
* `docs/purchasing.md` for procurement workflows;
* `docs/pos.md` for POS ingestion and blackout recovery;
* `docs/couriers.md` for Econt/Speedy and courier adapters;

Documentation must distinguish:

* framework behavior;
* adapter behavior;
* storefront behavior;
* production behavior;
* future optional extensions.

## 17. Non-Negotiable Invariants

* ERP is the operational source of truth.
* Storefronts are sales surfaces, not the business brain.
* Inventory uncertainty must be visible.
* Unknown barcodes must not silently create sellable stock.
* Unsafe items must not be published as sellable.
* Integrations must be logged.
* Courier/COD state must be explicit.
* POS blackout recovery must be reviewable.
* Public-facing users must not receive unrestricted ERP access.
* Public-facing state must not contain real business data.
* Secrets must not be committed.
* Backups must be restorable.
* Deployment must be reproducible.
* Recovery must be documented.
* Business-specific logic must not contaminate the generic APRP core.
* APRP exists for operations where spreadsheets are no longer infrastructure.
