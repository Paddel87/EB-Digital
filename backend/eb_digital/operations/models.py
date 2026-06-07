"""ORM-Modelle für ``backend/operations``.

Phase 2 Schritt 2.1: ``Operation`` (Einsatz, ohne direkte Tenant-FK gemäß
ADR-009 Invariante I1) und ``OperationAuditLog`` (Strukturskelett gemäß
ADR-008 — Multi-Disponent ohne Lead, vollständiges Audit-Log).

Phase 4 Schritt 4.3a:
  • ``Operation`` additiv um ``plausibility_threshold_m`` (ADR-017).
  • ``OperationArea`` — Polygon-Geometrie als JSONB-GeoJSON pro Einsatzraum.
  • ``OperationDispatcherParticipation`` — Disponenten-Teilnahme an Operation.
  • ``CustomerOrder`` / ``CustomerOrderItem`` / ``OrderAssignment`` — Bestell- und
    Auftragsdomäne. Tabellenname ``customer_order`` statt ``order``, weil
    ``order`` SQL-reserved ist; die Entity heißt in Diagrammen / ADRs ``Order``.

Die Operation↔Tenant-Verknüpfung läuft ausschließlich über
``operation_tenant_participation`` (siehe ``eb_digital.tenants.models``).
Spike-J-spezifische Bündel-FK-Spalten (``bundle_id`` an ``customer_order`` und
``order_assignment``) bleiben Schritt 4.3b vorbehalten; in 4.3a werden sie
**nicht** angelegt.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Final

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base, TimestampMixin

# Operation-Lebenszyklus. Whitelist-Constraint statt PostgreSQL-ENUM
# (Erweiterungen via einfacher ALTER-Migration).
OPERATION_STATUS_PLANNED: Final[str] = "planned"
OPERATION_STATUS_ACTIVE: Final[str] = "active"
OPERATION_STATUS_CLOSED: Final[str] = "closed"
ALLOWED_OPERATION_STATUS: Final[frozenset[str]] = frozenset(
    {OPERATION_STATUS_PLANNED, OPERATION_STATUS_ACTIVE, OPERATION_STATUS_CLOSED}
)

# Order-Status-Maschine (ADR-017 + Detail-Plan 4.3a-Frage 4A).
ORDER_STATUS_PENDING: Final[str] = "pending"
ORDER_STATUS_NEEDS_MODERATION: Final[str] = "needs_moderation"
ORDER_STATUS_ASSIGNED: Final[str] = "assigned"
ORDER_STATUS_IN_PROGRESS: Final[str] = "in_progress"
ORDER_STATUS_COMPLETED: Final[str] = "completed"
ORDER_STATUS_CANCELLED: Final[str] = "cancelled"
ALLOWED_ORDER_STATUS: Final[frozenset[str]] = frozenset(
    {
        ORDER_STATUS_PENDING,
        ORDER_STATUS_NEEDS_MODERATION,
        ORDER_STATUS_ASSIGNED,
        ORDER_STATUS_IN_PROGRESS,
        ORDER_STATUS_COMPLETED,
        ORDER_STATUS_CANCELLED,
    }
)

# OrderAssignment-Status. Eigene Maschine, weil Cancel/Complete-Pfade
# pro Assignment laufen können (z. B. Carer kann nicht erreichbar werden,
# Disponent reassignt).
ASSIGNMENT_STATUS_ASSIGNED: Final[str] = "assigned"
ASSIGNMENT_STATUS_IN_PROGRESS: Final[str] = "in_progress"
ASSIGNMENT_STATUS_COMPLETED: Final[str] = "completed"
ASSIGNMENT_STATUS_CANCELLED: Final[str] = "cancelled"
ALLOWED_ASSIGNMENT_STATUS: Final[frozenset[str]] = frozenset(
    {
        ASSIGNMENT_STATUS_ASSIGNED,
        ASSIGNMENT_STATUS_IN_PROGRESS,
        ASSIGNMENT_STATUS_COMPLETED,
        ASSIGNMENT_STATUS_CANCELLED,
    }
)

# OrderBundle-Status (ADR-018, Spike J). Bündel werden manuell vom
# Disponenten erzeugt; ``dissolved`` macht die Bündelung rückgängig
# (Orders zurück auf ``pending``), ``completed`` wird implizit gesetzt,
# sobald alle gebündelten Orders abgeschlossen sind (Detail-Plan 4.3b-2A).
# Ein ``cancelled``-Status ist Phase 1 bewusst nicht vorgesehen (4.3b-3A).
BUNDLE_STATUS_ACTIVE: Final[str] = "active"
BUNDLE_STATUS_COMPLETED: Final[str] = "completed"
BUNDLE_STATUS_DISSOLVED: Final[str] = "dissolved"
ALLOWED_BUNDLE_STATUS: Final[frozenset[str]] = frozenset(
    {BUNDLE_STATUS_ACTIVE, BUNDLE_STATUS_COMPLETED, BUNDLE_STATUS_DISSOLVED}
)

# Plausibility-Outcome (ADR-017). Wird im ``customer_order.plausibility_outcome``
# persistiert sowie in Audit-Log + Realtime-Payload referenziert.
PLAUSIBILITY_ACCEPTED: Final[str] = "ACCEPTED"
PLAUSIBILITY_MODERATION_NO_GPS: Final[str] = "MODERATION_NO_GPS"
PLAUSIBILITY_MODERATION_ACCURACY_TOO_LOW: Final[str] = "MODERATION_ACCURACY_TOO_LOW"
PLAUSIBILITY_MODERATION_OUT_OF_RANGE: Final[str] = "MODERATION_OUT_OF_RANGE"
ALLOWED_PLAUSIBILITY_OUTCOMES: Final[frozenset[str]] = frozenset(
    {
        PLAUSIBILITY_ACCEPTED,
        PLAUSIBILITY_MODERATION_NO_GPS,
        PLAUSIBILITY_MODERATION_ACCURACY_TOO_LOW,
        PLAUSIBILITY_MODERATION_OUT_OF_RANGE,
    }
)

# Plausibility-Algorithmus-Variante (ADR-017 nennt nur eine produktive
# Variante; das Feld bleibt für künftige A/B-Vergleiche im Audit-Log).
PLAUSIBILITY_VARIANT_DYNAMIC_2_ACCURACY: Final[str] = "dynamic_2_accuracy"
ALLOWED_PLAUSIBILITY_VARIANTS: Final[frozenset[str]] = frozenset(
    {PLAUSIBILITY_VARIANT_DYNAMIC_2_ACCURACY}
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Operation(Base, TimestampMixin):
    """Einsatz (zeitlich begrenzte Großlage).

    Verknüpfung zu Mandanten ausschließlich über
    ``operation_tenant_participation`` (Invariante I1, ADR-009). Phase 1
    hat genau einen Owner-Eintrag pro Operation; Phase X (Verbund-Modus)
    erweitert additiv um Participant-Einträge.

    Der ``access_code_hash`` speichert den Argon2id-Hash des Crockford-
    Base32-AccessCodes (ADR-005). Klartext wird nie persistiert; Verify
    läuft konstant-zeitig (Regel-006).

    Phase 4.3a additiv: ``plausibility_threshold_m`` — optionaler Operation-
    Override für den Plausibilitäts-Schwellenwert (ADR-017). ``NULL``
    bedeutet „benutze Tenant-Default".
    """

    __tablename__ = "operation"
    __table_args__ = (
        CheckConstraint(
            "status IN ('planned', 'active', 'closed')",
            name="status_allowed",
        ),
        CheckConstraint(
            "plausibility_threshold_m IS NULL OR plausibility_threshold_m BETWEEN 50 AND 50000",
            name="plausibility_threshold_m_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    # Stadt-/Region-Label vom Disponenten beim Eröffnen gesetzt
    # (z. B. „Bremen Innenstadt"). Quelle für ADR-006-Aggregat.
    city_label: Mapped[str] = mapped_column(String(120), nullable=False)
    # Signierter URL-Token für die Einsatzkraft-URL (Schritt 2.3 produktiv).
    # Generierung via ``itsdangerous.URLSafeSerializer`` mit Operation-UUID als
    # Payload; typische Länge ~80-100 Zeichen, daher ``String(255)`` (Spalte
    # wurde in Schritt 2.3 von ``String(64)`` auf ``String(255)`` geweitet).
    url_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    # Argon2id-PHC-Hash des AccessCodes; nullable, weil Code opt-in ist.
    access_code_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_code_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # ADR-017 Operation-Override. ``NULL`` ⇒ Tenant-Default greift.
    plausibility_threshold_m: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )


class OperationArea(Base, TimestampMixin):
    """Einsatzraum mit Polygon-Geometrie (Detail-Plan 4.3a-Frage 2A).

    Speicherung als **JSONB-GeoJSON-Polygon**: Form
    ``{"type": "Polygon", "coordinates": [[[lng, lat], …]]}``. Keine
    PostGIS-Extension — ADR-017 sieht App-Layer-Geometrie via Shapely vor;
    Volumen-Argument (wenige Räume pro Einsatz, kleine Punkt-Listen, <1 ms
    Hülle-Distanz pro Order) trägt die Wahl.

    ``area_index`` ist die operativ verwendete Reihenfolge ("Raum 1, Raum 2"
    im Disponenten-UI). Partial-UNIQUE garantiert Stabilität pro Operation.

    ``label`` ist die optionale Bezeichnung (z. B. "Marktplatz"); ``NULL``
    fällt auf "Einsatzraum N" zurück.
    """

    __tablename__ = "operation_area"
    __table_args__ = (
        UniqueConstraint(
            "operation_id",
            "area_index",
            name="uq_operation_area_operation_id_area_index",
        ),
        Index(
            "ix_operation_area_operation_id",
            "operation_id",
        ),
        # Schema-Disziplin im Polygon-JSONB — Shapely tut den Rest im
        # App-Layer; das CHECK ist Defense-in-Depth gegen versehentliche
        # Klar-String-Inserts.
        CheckConstraint(
            "polygon ? 'type' AND polygon ? 'coordinates'",
            name="polygon_geojson_keys",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operation.id", ondelete="CASCADE"),
        nullable=False,
    )
    area_index: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    polygon: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class OperationDispatcherParticipation(Base):
    """Teilnahme eines Disponenten an einem Einsatz (ADR-008-Kontext).

    Eine Zeile pro (operation, dispatcher). ``joined_at`` ist der erste
    Eintritt; ``left_at`` ist optional (Disponent kann am Einsatz bleiben
    bis Operation-Ende; bei explizitem Verlassen wird ``left_at`` gesetzt).
    Wiederbeitritte werden über ein zusätzliches Insert nicht abgebildet —
    ``left_at`` wird per ``UPDATE`` zurückgesetzt (PK verhindert Duplikate).

    Quelle für ``peak_active_dispatchers`` im ADR-006-Aggregat: COUNT der
    Zeilen mit ``left_at IS NULL`` zum Stichzeitpunkt.
    """

    __tablename__ = "operation_dispatcher_participation"

    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operation.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dispatcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )


class CustomerOrder(Base, TimestampMixin):
    """Bestellung einer Einsatzkraft (Flow F2, ADR-017-Plausibility).

    Tabellenname ``customer_order`` — ``order`` ist SQL-reserved und
    bricht ``\\d`` / ungequotete Queries. Die Entity bleibt in
    Architektur-Diagrammen ``Order`` (siehe ``architecture.md`` §7).

    ``anonymous_session_id`` ist ``SET NULL`` beim Session-Cleanup:
    Bestellung bleibt für Aggregat- und Audit-Zwecke erhalten, der
    Personenbezug verschwindet (DSGVO-konsistent).

    ``location_lat`` / ``location_lng`` / ``location_accuracy_m`` werden
    additiv von der Einsatzkraft-PWA übermittelt; ``location_text`` ist
    der Fallback bei verweigerter GPS-Permission oder Funkloch.

    Die ``plausibility_*``-Felder werden zum Zeitpunkt der Anlage durch
    ``PlausibilityChecker`` aus ``backend/geo`` gesetzt und sind danach
    immutable (Audit-Spur). Bei Moderations-Outcome wird der Order-Status
    auf ``needs_moderation`` gesetzt; ein Disponent kann via
    ``ApproveLowPlausibilityOrder`` auf ``pending`` befördern. Die
    Audit-Spur (``moderation_actor_dispatcher_id``, ``moderation_at``)
    bleibt als historischer Beleg.

    Spike-J (4.3b) ergänzt additiv ``bundle_id`` als nullable FK auf
    ``order_bundle``; in 4.3a noch nicht vorhanden.
    """

    __tablename__ = "customer_order"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'needs_moderation', 'assigned', "
            "'in_progress', 'completed', 'cancelled')",
            name="status_allowed",
        ),
        CheckConstraint(
            "plausibility_outcome IN ('ACCEPTED', 'MODERATION_NO_GPS', "
            "'MODERATION_ACCURACY_TOO_LOW', 'MODERATION_OUT_OF_RANGE')",
            name="plausibility_outcome_allowed",
        ),
        # Entweder beide GPS-Koordinaten gesetzt oder keine.
        CheckConstraint(
            "(location_lat IS NULL) = (location_lng IS NULL)",
            name="location_lat_lng_both_or_none",
        ),
        CheckConstraint(
            "location_lat IS NULL OR location_lat BETWEEN -90 AND 90",
            name="location_lat_range",
        ),
        CheckConstraint(
            "location_lng IS NULL OR location_lng BETWEEN -180 AND 180",
            name="location_lng_range",
        ),
        CheckConstraint(
            "location_accuracy_m IS NULL OR location_accuracy_m > 0",
            name="location_accuracy_m_positive",
        ),
        # Bestellung braucht eine Ortsangabe: entweder GPS oder Text-
        # Standort. Sonst kann keine Plausibility-Aussage getroffen werden.
        CheckConstraint(
            "location_lat IS NOT NULL OR location_text IS NOT NULL",
            name="location_gps_or_text_required",
        ),
        # Wirksame Plausibilitäts-Schwelle pro Order (ADR-017 — aus
        # dreistufiger Hierarchie aufgelöst).
        CheckConstraint(
            "plausibility_threshold_m BETWEEN 50 AND 50000",
            name="plausibility_threshold_m_range",
        ),
        # Hot-Path: „Orders einer Operation nach Status filtern".
        Index(
            "ix_customer_order_operation_id_status",
            "operation_id",
            "status",
        ),
        Index(
            "ix_customer_order_operation_id_placed_at",
            "operation_id",
            "placed_at",
        ),
        # Spike-J (4.3b): Lookup „Orders eines Bündels".
        Index(
            "ix_customer_order_bundle_id",
            "bundle_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operation.id", ondelete="CASCADE"),
        nullable=False,
    )
    anonymous_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("anonymous_session.id", ondelete="SET NULL"),
        nullable=True,
    )
    placed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # ADR-017-Audit-Felder. Werden bei Order-Anlage gesetzt und sind
    # danach unveränderlich.
    plausibility_outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    plausibility_distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    plausibility_threshold_m: Mapped[int] = mapped_column(Integer, nullable=False)
    plausibility_variant: Mapped[str] = mapped_column(String(40), nullable=False)
    # Moderations-Spur — nullable, wird beim Approve gesetzt.
    moderation_actor_dispatcher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="SET NULL"),
        nullable=True,
    )
    moderation_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # Spike-J (4.3b): nullable FK auf ``order_bundle``. ``NULL`` ⇒ Order ist
    # nicht gebündelt. Kein ondelete-Cascade — Bündel werden nie zeilenweise
    # gelöscht (ADR-018 / Detail-Plan 4.3b-1A).
    bundle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("order_bundle.id"),
        nullable=True,
    )


class CustomerOrderItem(Base):
    """Bestellte Catalog-Position (analog zu ``vehicle_loadout_item`` aus 4.2).

    Genau eine Catalog-Referenz pro Eintrag — entweder Base-Item oder
    Tenant-Extension (CHECK ``exactly_one_ref``). ``RESTRICT`` auf den FKs
    verhindert Catalog-Löschung, solange noch Orders darauf verweisen.
    """

    __tablename__ = "customer_order_item"
    __table_args__ = (
        CheckConstraint(
            "(base_item_id IS NOT NULL AND tenant_extension_id IS NULL) "
            "OR (base_item_id IS NULL AND tenant_extension_id IS NOT NULL)",
            name="exactly_one_ref",
        ),
        CheckConstraint(
            "quantity > 0",
            name="quantity_positive",
        ),
        Index(
            "ix_customer_order_item_order_id",
            "order_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_order.id", ondelete="CASCADE"),
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
        default=_utcnow,
    )


class OrderAssignment(Base, TimestampMixin):
    """Zuweisung eines Fahrzeugs zu einer Bestellung (S4 / I3).

    Aktive Assignment-Disziplin: pro ``order_id`` höchstens **ein** Eintrag
    mit Status ``assigned`` oder ``in_progress`` (Partial-UNIQUE). Cancelled
    Assignments bleiben als Historie sichtbar; ein Reassign legt einen
    neuen Eintrag an.

    ``vehicle_id`` ist ``RESTRICT`` — ein zugewiesenes Fahrzeug darf nicht
    aus dem System gelöscht werden, solange Assignments existieren.

    ``dispatcher_id`` referenziert den anweisenden Disponenten (Audit-
    Spur). ``RESTRICT`` aus demselben Grund.

    Spike-J (4.3b) ergänzt additiv ``bundle_id`` als nullable FK; in 4.3a
    noch nicht vorhanden.
    """

    __tablename__ = "order_assignment"
    __table_args__ = (
        CheckConstraint(
            "status IN ('assigned', 'in_progress', 'completed', 'cancelled')",
            name="status_allowed",
        ),
        # Höchstens ein aktives Assignment pro Order — kein
        # gleichzeitiges Doppelt-Disponieren.
        Index(
            "ix_order_assignment_order_id_active_unique",
            "order_id",
            unique=True,
            postgresql_where=text("status IN ('assigned', 'in_progress')"),
        ),
        Index(
            "ix_order_assignment_vehicle_id",
            "vehicle_id",
        ),
        Index(
            "ix_order_assignment_bundle_id",
            "bundle_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_order.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle.id", ondelete="RESTRICT"),
        nullable=False,
    )
    dispatcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # Spike-J (4.3b): nullable FK auf ``order_bundle``. Bei Bündel-Assignment
    # tragen alle N Assignments dieselbe ``bundle_id`` und dasselbe
    # ``vehicle_id`` (= Versorgungs-Transporter). ``NULL`` bei
    # nicht-gebündelten Assignments (ADR-018 S4-Bündel-Mapping).
    bundle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("order_bundle.id"),
        nullable=True,
    )


class OrderBundle(Base, TimestampMixin):
    """Bündel mehrerer Bestellungen für einen Versorgungs-Transporter (ADR-018).

    Großbestellungs-Modus: ein Disponent bündelt manuell ≥ 2 ``pending``-
    Orders auf einen Versorgungs-Transporter mit ``mode='large_order'``
    (Detail-Plan 4.3b). Jede gebündelte Order bekommt ein eigenes
    ``OrderAssignment`` mit identischer ``bundle_id`` und identischem
    ``vehicle_id``.

    ``status`` durchläuft ``active → completed`` (implizit, wenn alle
    Orders abgeschlossen sind) bzw. ``active → dissolved`` (Disponent löst
    auf; Orders zurück auf ``pending``). Bündel werden nie zeilenweise
    gelöscht — nur Status-Übergänge.

    ``created_by_dispatcher_id`` ist die Audit-Spur des anlegenden
    Disponenten (``RESTRICT``).
    """

    __tablename__ = "order_bundle"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'dissolved')",
            name="status_allowed",
        ),
        Index(
            "ix_order_bundle_operation_id",
            "operation_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operation.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by_dispatcher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)


class OperationAuditLog(Base):
    """Audit-Log-Eintrag für eine Operation (ADR-008).

    Eine Zeile pro destruktiver oder konfigurierender Aktion. Audit-Log
    ist immutable — kein ``updated_at``. ``actor_dispatcher_id`` ist
    nullable und ``ON DELETE SET NULL``, damit DSGVO-Anonymisierung den
    Personenbezug entfernen kann, ohne den Audit-Eintrag selbst zu
    löschen.

    Das Action-Vokabular wächst mit Phase 4 (``backend/operations`` Use-
    Cases); deshalb in Phase 2.1 kein DB-CHECK auf ``action_type``,
    sondern eine String-Spalte. Ein CHECK-Constraint kann später additiv
    via Migration ergänzt werden, sobald das Vokabular stabil ist.
    """

    __tablename__ = "operation_audit_log"
    __table_args__ = (
        # Standard-Query: „letzte Audit-Einträge einer Operation".
        Index(
            "ix_operation_audit_log_operation_id_at",
            "operation_id",
            "at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operation.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_dispatcher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="SET NULL"),
        nullable=True,
    )
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    target_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    # Convention: bei Operation-Level-Aktionen ``target_id = operation_id``.
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    # Aktion-spezifische Detail-Daten ohne PII (ADR-008-Konsequenz).
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


__all__ = [
    "ALLOWED_ASSIGNMENT_STATUS",
    "ALLOWED_BUNDLE_STATUS",
    "ALLOWED_OPERATION_STATUS",
    "ALLOWED_ORDER_STATUS",
    "ALLOWED_PLAUSIBILITY_OUTCOMES",
    "ALLOWED_PLAUSIBILITY_VARIANTS",
    "ASSIGNMENT_STATUS_ASSIGNED",
    "ASSIGNMENT_STATUS_CANCELLED",
    "ASSIGNMENT_STATUS_COMPLETED",
    "ASSIGNMENT_STATUS_IN_PROGRESS",
    "BUNDLE_STATUS_ACTIVE",
    "BUNDLE_STATUS_COMPLETED",
    "BUNDLE_STATUS_DISSOLVED",
    "OPERATION_STATUS_ACTIVE",
    "OPERATION_STATUS_CLOSED",
    "OPERATION_STATUS_PLANNED",
    "ORDER_STATUS_ASSIGNED",
    "ORDER_STATUS_CANCELLED",
    "ORDER_STATUS_COMPLETED",
    "ORDER_STATUS_IN_PROGRESS",
    "ORDER_STATUS_NEEDS_MODERATION",
    "ORDER_STATUS_PENDING",
    "PLAUSIBILITY_ACCEPTED",
    "PLAUSIBILITY_MODERATION_ACCURACY_TOO_LOW",
    "PLAUSIBILITY_MODERATION_NO_GPS",
    "PLAUSIBILITY_MODERATION_OUT_OF_RANGE",
    "PLAUSIBILITY_VARIANT_DYNAMIC_2_ACCURACY",
    "CustomerOrder",
    "CustomerOrderItem",
    "Operation",
    "OperationArea",
    "OperationAuditLog",
    "OperationDispatcherParticipation",
    "OrderAssignment",
    "OrderBundle",
]
