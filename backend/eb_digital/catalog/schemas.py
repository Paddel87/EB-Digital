"""Pydantic-Schemas für ``backend/catalog``-API.

Eigene Datei (statt inline in ``api.py`` wie in ``tenants``), weil die
Catalog-API zwölf Schemas trägt — drei Read/Create/Update-Paare plus
``ResolvedCatalogItem`` für den Resolver-Output.

Naming-Konvention: Modell-Suffix gibt die Rolle an —
``…Create`` (POST-Body), ``…Update`` (PATCH-Body), ``…Response``
(GET-Response). Felder snake_case, konsistent zur restlichen API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Final

from pydantic import BaseModel, Field

# Längen-Constraints zentralisiert, damit Migration + Pydantic + Tests
# dieselben Grenzen führen. Müssen mit den String-Längen in
# ``models.py`` übereinstimmen.
MAX_CATEGORY_NAME_LEN: Final[int] = 64
MAX_ITEM_NAME_LEN: Final[int] = 120
MAX_UNIT_LEN: Final[int] = 16
MAX_UNIT_LABEL_LEN: Final[int] = 32


# ─── Categories ──────────────────────────────────────────────────────────────


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_CATEGORY_NAME_LEN)


class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str


# ─── Base Items ──────────────────────────────────────────────────────────────


class BaseItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_ITEM_NAME_LEN)
    unit: str = Field(min_length=1, max_length=MAX_UNIT_LEN)
    default_unit_label: str = Field(min_length=1, max_length=MAX_UNIT_LABEL_LEN)
    category_id: str
    description: str | None = Field(default=None, max_length=4096)


class BaseItemUpdate(BaseModel):
    """PATCH-Body für Base-Items. Nur gesetzte Felder werden geändert.

    ``is_active`` separat aussteuerbar, damit Soft-Delete via PATCH
    möglich ist (oder explizit über ``DELETE``-Endpoint).
    """

    name: str | None = Field(default=None, min_length=1, max_length=MAX_ITEM_NAME_LEN)
    unit: str | None = Field(default=None, min_length=1, max_length=MAX_UNIT_LEN)
    default_unit_label: str | None = Field(
        default=None, min_length=1, max_length=MAX_UNIT_LABEL_LEN
    )
    category_id: str | None = None
    description: str | None = Field(default=None, max_length=4096)
    is_active: bool | None = None


class BaseItemResponse(BaseModel):
    id: str
    name: str
    unit: str
    default_unit_label: str
    description: str | None
    category_id: str
    is_active: bool
    created_at: str
    updated_at: str


# ─── Tenant Extensions ───────────────────────────────────────────────────────


class TenantExtensionOverrideCreate(BaseModel):
    """POST-Body für einen Override eines Base-Items.

    ``override_name`` / ``override_unit_label`` sind optional — wenn
    beide NULL bleiben, wirkt der Override nur über ``is_disabled``
    (das später per Update gesetzt wird).
    """

    base_item_id: str
    override_name: str | None = Field(default=None, min_length=1, max_length=MAX_ITEM_NAME_LEN)
    override_unit_label: str | None = Field(
        default=None, min_length=1, max_length=MAX_UNIT_LABEL_LEN
    )


class TenantExtensionOwnCreate(BaseModel):
    """POST-Body für ein eigenständiges Tenant-Item.

    Alle vier Pflichtfelder sind erforderlich (DB-CHECK-Constraint
    ``mode_constraint``). ``base_item_id`` wird vom Endpoint ignoriert
    bzw. nicht gesetzt.
    """

    name: str = Field(min_length=1, max_length=MAX_ITEM_NAME_LEN)
    unit: str = Field(min_length=1, max_length=MAX_UNIT_LEN)
    default_unit_label: str = Field(min_length=1, max_length=MAX_UNIT_LABEL_LEN)
    category_id: str
    description: str | None = Field(default=None, max_length=4096)


class TenantExtensionUpdate(BaseModel):
    """PATCH-Body für Tenant-Extensions.

    Welche Felder geändert werden dürfen, hängt vom Modus ab — der
    Endpoint validiert das gegen den existierenden Eintrag. Hier nur
    die Pydantic-Schicht (typ-/length-Check).
    """

    # Override-Modus
    override_name: str | None = Field(default=None, min_length=1, max_length=MAX_ITEM_NAME_LEN)
    override_unit_label: str | None = Field(
        default=None, min_length=1, max_length=MAX_UNIT_LABEL_LEN
    )
    # Eigenständig-Modus
    name: str | None = Field(default=None, min_length=1, max_length=MAX_ITEM_NAME_LEN)
    unit: str | None = Field(default=None, min_length=1, max_length=MAX_UNIT_LEN)
    default_unit_label: str | None = Field(
        default=None, min_length=1, max_length=MAX_UNIT_LABEL_LEN
    )
    category_id: str | None = None
    description: str | None = Field(default=None, max_length=4096)
    # Beide Modi
    is_disabled: bool | None = None


class TenantExtensionResponse(BaseModel):
    id: str
    tenant_id: str
    base_item_id: str | None
    name: str | None
    unit: str | None
    default_unit_label: str | None
    description: str | None
    category_id: str | None
    override_name: str | None
    override_unit_label: str | None
    is_disabled: bool
    created_at: str
    updated_at: str


# ─── Resolver-Output ─────────────────────────────────────────────────────────


class ResolvedCatalogItem(BaseModel):
    """Effektiver Catalog-Eintrag aus Resolver-Sicht.

    ``source`` unterscheidet Base-Items (``base``) von eigenständigen
    Tenant-Items (``tenant_own``); Override-Items werden als ``base``
    geliefert, ihre Override-Werte sind bereits in ``name`` /
    ``default_unit_label`` einkomponiert.
    """

    id: str
    """ID des Resolver-Eintrags. Bei ``source=base`` die Base-ID; bei
    ``source=tenant_own`` die Extension-ID."""

    base_item_id: str | None
    """Für Override-Einträge: die ID des Base-Items, das überschrieben
    wurde. Für eigenständige Tenant-Items: NULL."""

    source: str
    """Eintrags-Herkunft: ``base`` oder ``tenant_own``."""

    name: str
    unit: str
    default_unit_label: str
    description: str | None
    category_id: str
    category_name: str


# Hilfsfunktionen für die Serialisierung von Datetime → ISO-String
# (konsistent mit ``TenantResponse.from_tenant``-Pattern).


def iso(dt: datetime) -> str:
    """Datetime → ISO-8601 mit Zeitzone (UTC)."""
    return dt.isoformat()


__all__ = [
    "MAX_CATEGORY_NAME_LEN",
    "MAX_ITEM_NAME_LEN",
    "MAX_UNIT_LABEL_LEN",
    "MAX_UNIT_LEN",
    "BaseItemCreate",
    "BaseItemResponse",
    "BaseItemUpdate",
    "CategoryCreate",
    "CategoryResponse",
    "ResolvedCatalogItem",
    "TenantExtensionOverrideCreate",
    "TenantExtensionOwnCreate",
    "TenantExtensionResponse",
    "TenantExtensionUpdate",
    "iso",
]
