"""ORM-Modelle für ``backend/fleet`` (Phase 4 Schritt 4.2).

Fünf Tabellen, siehe Modul-Docstring. Wichtige Constraints:

  • ``vehicle.mode_constraint`` — Typ-/Modus-Kombi: nur Supply-Transporter
    haben ein Modus-Feld; reguläre Fahrzeuge haben ``mode IS NULL``.
  • ``vehicle_loadout_item.exactly_one_ref`` — Beladungs-Position
    referenziert entweder ein Base- oder ein Tenant-Extension-Item,
    niemals beides oder keines.
  • ``vehicle_loadout_item.quantity_positive`` — Mengen > 0.
  • Partial-UNIQUE-Indizes verhindern Doppel-Einträge pro Loadout pro
    Base- bzw. Tenant-Extension-Ref.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base, TimestampMixin

# Erlaubte Werte für ``vehicle.type`` und ``vehicle.mode``.
VEHICLE_TYPE_REGULAR = "regular"
VEHICLE_TYPE_SUPPLY_TRANSPORTER = "supply_transporter"
ALLOWED_VEHICLE_TYPES = frozenset({VEHICLE_TYPE_REGULAR, VEHICLE_TYPE_SUPPLY_TRANSPORTER})

SUPPLY_MODE_OFF = "off"
SUPPLY_MODE_MOBILE_SUPPLY = "mobile_supply"
SUPPLY_MODE_LARGE_ORDER = "large_order"
ALLOWED_SUPPLY_MODES = frozenset(
    {SUPPLY_MODE_OFF, SUPPLY_MODE_MOBILE_SUPPLY, SUPPLY_MODE_LARGE_ORDER}
)


class Vehicle(Base, TimestampMixin):
    """Fahrzeug — mandanten-gebunden, mit Typ-Spalte (regulär vs. Versorgungs-Transporter).

    Single Table Inheritance über ``type``; nur Supply-Transporter führen
    ein ``mode``-Feld (Default ``off`` beim Anlegen, in ``mobile_supply``
    oder ``large_order`` wechselbar via ``UpdateSupplyTransporterMode``).
    Reguläre Fahrzeuge haben ``mode IS NULL``.

    ``ondelete='CASCADE'`` auf ``tenant_id`` ist konsistent mit
    Catalog-Tenant-Extensions: die Deactivation-Pfade in
    ``backend/tenants`` löschen Tenants nicht direkt, daher ist CASCADE
    hier kein DSGVO-Risiko, sondern Defense-in-Depth.

    ``is_active=FALSE`` ist Soft-Delete; das Fahrzeug erscheint nicht
    mehr in Standard-Listen, bleibt aber für historische Auswertung
    erhalten (z. B. Loadout-History referenziert weiter).
    """

    __tablename__ = "vehicle"
    __table_args__ = (
        CheckConstraint(
            "type IN ('regular', 'supply_transporter')",
            name="type_valid",
        ),
        # Single Table Inheritance: Modus-Feld nur für Supply-Transporter.
        CheckConstraint(
            "("
            "    type = 'supply_transporter' "
            "    AND mode IN ('off', 'mobile_supply', 'large_order')"
            ") OR ("
            "    type = 'regular' "
            "    AND mode IS NULL"
            ")",
            name="type_mode_constraint",
        ),
        # Tenant-Scope-Lookups.
        Index("ix_vehicle_tenant_id", "tenant_id"),
        # Default-Listing filtert auf aktive Fahrzeuge.
        Index(
            "ix_vehicle_tenant_id_active",
            "tenant_id",
            postgresql_where=text("is_active = TRUE"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    license_plate: Mapped[str | None] = mapped_column(String(32), nullable=True)
    capacity_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class TenantHeadOffice(Base, TimestampMixin):
    """Geschäftsstelle (HeadOffice) — 1:1 zu ``Tenant``.

    Stationäre Hauptversorgungsstelle des Mandanten, von der Schichten
    starten. Phase 1: genau eine pro Tenant; PK ist ``tenant_id`` (kein
    eigener Surrogat-Key — eine spätere n:1-Erweiterung würde additiv
    eine eigene Tabelle bekommen).

    Range-Checks auf Lat/Lng dupliziert die Pydantic-Validation auf
    DB-Ebene als Sicherheitsnetz gegen direkten SQL-Eingriff.
    """

    __tablename__ = "tenant_head_office"
    __table_args__ = (
        CheckConstraint(
            "lat BETWEEN -90 AND 90",
            name="lat_range",
        ),
        CheckConstraint(
            "lng BETWEEN -180 AND 180",
            name="lng_range",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        primary_key=True,
    )
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)


class VehicleLoadout(Base, TimestampMixin):
    """Aktueller Beladungs-Snapshot eines Fahrzeugs (1:1 zu ``Vehicle``).

    UNIQUE auf ``vehicle_id`` durchsetzt die 1:1-Beziehung. Bei jedem
    ``SetLoadout``-Use-Case wird der vorhandene Snapshot in
    ``vehicle_loadout_history`` als Frozen JSONB kopiert, bevor die
    Items dieser Tabelle ersetzt werden.

    ``recorded_by_dispatcher_id`` mit ``ondelete='RESTRICT'`` — Dispatcher-
    Lösch-Pfade in ``backend/tenants`` müssen Loadouts explizit umhängen
    oder löschen, kein automatischer Cascade.
    """

    __tablename__ = "vehicle_loadout"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    recorded_by_dispatcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="RESTRICT"),
        nullable=False,
    )


class VehicleLoadoutItem(Base):
    """Beladungs-Position in einem ``VehicleLoadout``.

    Item-Referenz ist exklusiv: entweder ``base_item_id`` (Plattform-
    Standard-Item) ODER ``tenant_extension_id`` (mandanten-eigenständiges
    oder per Tenant-Override personalisiertes Item). Tenant-Extensions
    müssen zum Vehicle-Tenant gehören; das prüft der Use-Case, weil die
    DB-CHECK-Klausel diese Cross-Table-Beziehung nicht ausdrücken kann.

    Partial-UNIQUE-Indizes verhindern Doppel-Einträge pro Loadout je Ref-
    Typ. Mengen sind streng positiv (``quantity > 0``); zur Bestands-
    Reduktion auf Null gehört ein expliziter Item-Remove im Use-Case.

    Audit-Zeitstempel beschränkt auf ``created_at`` (kein ``updated_at``),
    weil Items unveränderlich sind — eine Mengen-Korrektur erzeugt einen
    neuen Loadout-Snapshot (= neuer Eintrag, alter Stand in History).
    """

    __tablename__ = "vehicle_loadout_item"
    __table_args__ = (
        CheckConstraint(
            "("
            "    base_item_id IS NOT NULL AND tenant_extension_id IS NULL"
            ") OR ("
            "    base_item_id IS NULL AND tenant_extension_id IS NOT NULL"
            ")",
            name="exactly_one_ref",
        ),
        CheckConstraint(
            "quantity > 0",
            name="quantity_positive",
        ),
        # Pro Loadout darf jedes Base-Item höchstens einmal erscheinen.
        Index(
            "ix_vehicle_loadout_item_loadout_base_unique",
            "loadout_id",
            "base_item_id",
            unique=True,
            postgresql_where=text("base_item_id IS NOT NULL"),
        ),
        # Pro Loadout darf jede Tenant-Extension höchstens einmal erscheinen.
        Index(
            "ix_vehicle_loadout_item_loadout_extension_unique",
            "loadout_id",
            "tenant_extension_id",
            unique=True,
            postgresql_where=text("tenant_extension_id IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    loadout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle_loadout.id", ondelete="CASCADE"),
        nullable=False,
    )
    base_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_item_base.id", ondelete="RESTRICT"),
        nullable=True,
    )
    tenant_extension_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_item_tenant_extension.id", ondelete="RESTRICT"),
        nullable=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class VehicleLoadoutHistory(Base):
    """Append-only Snapshot vergangener Beladungen pro Fahrzeug.

    Bei jedem ``SetLoadout`` wird der aktuelle Snapshot (vor dem Replace)
    in diese Tabelle kopiert. ``items`` ist ein Frozen JSONB-Array mit den
    Item-Daten zum Snapshot-Zeitpunkt — eingefroren, weil das referenzierte
    Catalog-Item später deaktiviert, umbenannt oder gelöscht werden kann.
    Ein Frozen JSONB-Eintrag entkoppelt History von Catalog-Veränderungen.

    Indizes für „letzte N Snapshots eines Fahrzeugs" (DESC nach
    ``recorded_at``).
    """

    __tablename__ = "vehicle_loadout_history"
    __table_args__ = (
        Index(
            "ix_vehicle_loadout_history_vehicle_id_recorded_at",
            "vehicle_id",
            "recorded_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle.id", ondelete="CASCADE"),
        nullable=False,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    recorded_by_dispatcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # Frozen Snapshot der Items: [{"ref_kind": "base|extension", "ref_id": "...",
    # "quantity": 5, "name_at_snapshot": "...", "unit_at_snapshot": "..."}]
    items: Mapped[Any] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


__all__ = [
    "ALLOWED_SUPPLY_MODES",
    "ALLOWED_VEHICLE_TYPES",
    "SUPPLY_MODE_LARGE_ORDER",
    "SUPPLY_MODE_MOBILE_SUPPLY",
    "SUPPLY_MODE_OFF",
    "VEHICLE_TYPE_REGULAR",
    "VEHICLE_TYPE_SUPPLY_TRANSPORTER",
    "TenantHeadOffice",
    "Vehicle",
    "VehicleLoadout",
    "VehicleLoadoutHistory",
    "VehicleLoadoutItem",
]
