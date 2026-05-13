"""Core APRP business contract definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

MODULE_NAME: Final[str] = "APRP"


@dataclass(frozen=True)
class DoctypeContract:
    """Describe one core business doctype surface."""

    name: str
    workspace: str
    fields: tuple[str, ...]
    roles: tuple[str, ...]
    purpose: str


@dataclass(frozen=True)
class PermissionDomain:
    """Describe one permission boundary for the APRP core."""

    name: str
    roles: tuple[str, ...]
    scope: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class WorkspaceSection:
    """Describe one workspace grouping for the APRP core."""

    name: str
    doctypes: tuple[str, ...]
    purpose: str


CORE_DOCTYPES: Final[tuple[DoctypeContract, ...]] = (
    DoctypeContract(
        name="APRP Product",
        workspace="Inventory",
        fields=(
            "internal_id",
            "product_name",
            "barcode",
            "supplier",
            "tax_profile",
            "price_list",
            "sellable",
            "publishable",
            "notes",
        ),
        roles=("APRP Operator", "APRP Staff"),
        purpose="Stable product identity and stock-facing metadata.",
    ),
    DoctypeContract(
        name="APRP Supplier",
        workspace="Purchasing",
        fields=(
            "supplier_name",
            "vat_id",
            "email",
            "phone",
            "country",
            "default_vat_rate",
            "notes",
        ),
        roles=("APRP Operator", "APRP Staff"),
        purpose="Supplier identity and procurement-facing contact data.",
    ),
    DoctypeContract(
        name="APRP Customer",
        workspace="Operations",
        fields=(
            "customer_name",
            "phone",
            "email",
            "delivery_address",
            "country",
            "notes",
        ),
        roles=("APRP Operator", "APRP Staff"),
        purpose="Shared customer master data for downstream sales flows.",
    ),
    DoctypeContract(
        name="APRP Location",
        workspace="Inventory",
        fields=(
            "location_name",
            "company",
            "warehouse",
            "address",
            "notes",
        ),
        roles=("APRP Operator", "APRP Staff"),
        purpose="Physical location identity and warehouse binding.",
    ),
    DoctypeContract(
        name="APRP Warehouse Policy",
        workspace="Inventory",
        fields=(
            "policy_name",
            "location",
            "warehouse",
            "purpose",
            "priority",
            "active",
            "notes",
        ),
        roles=("APRP Operator", "APRP Staff"),
        purpose="Explicit warehouse purpose and routing policy.",
    ),
    DoctypeContract(
        name="APRP Tax Profile",
        workspace="Purchasing",
        fields=(
            "tax_profile_name",
            "country",
            "vat_rate",
            "sales_vat_rate",
            "purchase_vat_rate",
            "notes",
        ),
        roles=("APRP Operator",),
        purpose="Tax and VAT defaults for purchase and sales planning.",
    ),
    DoctypeContract(
        name="APRP Price List",
        workspace="Purchasing",
        fields=(
            "price_list_name",
            "currency",
            "customer_group",
            "territory",
            "notes",
        ),
        roles=("APRP Operator", "APRP Staff"),
        purpose="Price-list identity for procurement and sales setup.",
    ),
)

PERMISSION_DOMAINS: Final[tuple[PermissionDomain, ...]] = (
    PermissionDomain(
        name="operator",
        roles=("APRP Operator", "System Manager"),
        scope="global",
        capabilities=(
            "manage-master-data",
            "manage-warehouse-policy",
            "reconcile-inventory",
            "approve-procurement",
        ),
    ),
    PermissionDomain(
        name="staff",
        roles=("APRP Staff",),
        scope="module",
        capabilities=(
            "capture-intake",
            "draft-procurement",
            "manage-location-work",
        ),
    ),
    PermissionDomain(
        name="location-scoped-user",
        roles=("APRP Location User",),
        scope="location",
        capabilities=(
            "view-location-stock",
            "submit-location-events",
            "read-location-master-data",
        ),
    ),
)

WORKSPACE_SECTIONS: Final[tuple[WorkspaceSection, ...]] = (
    WorkspaceSection(
        name="Inventory",
        doctypes=(
            "APRP Product",
            "APRP Location",
            "APRP Warehouse Policy",
        ),
        purpose="Inventory identity, locations, and stock policy.",
    ),
    WorkspaceSection(
        name="Purchasing",
        doctypes=(
            "APRP Supplier",
            "APRP Tax Profile",
            "APRP Price List",
        ),
        purpose="Supplier, tax, and price-list governance.",
    ),
    WorkspaceSection(
        name="Operations",
        doctypes=("APRP Customer",),
        purpose="Shared customer master data.",
    ),
)


def core_doctype_names() -> tuple[str, ...]:
    """Return the stable list of APRP core doctypes."""

    return tuple(contract.name for contract in CORE_DOCTYPES)


def permission_domain_names() -> tuple[str, ...]:
    """Return the stable list of APRP permission domains."""

    return tuple(domain.name for domain in PERMISSION_DOMAINS)


def workspace_names() -> tuple[str, ...]:
    """Return the stable list of APRP workspace sections."""

    return tuple(section.name for section in WORKSPACE_SECTIONS)


__all__ = [
    "CORE_DOCTYPES",
    "DoctypeContract",
    "MODULE_NAME",
    "PERMISSION_DOMAINS",
    "PermissionDomain",
    "WORKSPACE_SECTIONS",
    "WorkspaceSection",
    "core_doctype_names",
    "permission_domain_names",
    "workspace_names",
]
