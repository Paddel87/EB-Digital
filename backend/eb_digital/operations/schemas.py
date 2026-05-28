"""Pydantic-Schemas für ``backend/operations`` (Schritt 4.3a).

Sub-Surface ``S8e`` (``/api/operations/*``) und Sub-Surface ``S2c``
(``/api/anon/{operation_url}/order``) gemäß Rollen-Matrix Frage 9A.

Schemas trennen klar zwischen Eingangs- (``*Request`` / ``*In``) und
Ausgangs- (``*Response`` / ``*Out``) DTOs. Interne SQLAlchemy-Modelle
werden nie direkt serialisiert; die Konvertierung läuft im API-Layer.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Annotated, Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ───────────────────────────────────────────────────────────────────────
# Polygon (GeoJSON)
# ───────────────────────────────────────────────────────────────────────

# GeoJSON-Polygon — Wir validieren in zwei Stufen:
#   1) Strukturelle Pflichtfelder (``type``, ``coordinates``)
#   2) Form: erstes Ring (außen) hat ≥ 4 Punkte (geschlossener Polygon),
#      jeder Punkt ist ``[lng, lat]`` mit numerischen Werten im
#      gültigen Bereich.
_GEOJSON_POLYGON_TYPE: Final[str] = "Polygon"


class Polygon(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["Polygon"]
    coordinates: list[list[list[float]]]

    @model_validator(mode="after")
    def _validate_geometry(self) -> Polygon:
        if not self.coordinates:
            raise ValueError("Polygon needs at least one ring (outer)")
        outer = self.coordinates[0]
        if len(outer) < 4:
            raise ValueError("Polygon outer ring needs ≥ 4 points (closed ring)")
        if outer[0] != outer[-1]:
            raise ValueError("Polygon outer ring must be closed (first == last)")
        for point in outer:
            if len(point) != 2:
                raise ValueError("Polygon points must be [lng, lat]")
            lng, lat = point
            if not (-180.0 <= lng <= 180.0):
                raise ValueError(f"Longitude out of range: {lng}")
            if not (-90.0 <= lat <= 90.0):
                raise ValueError(f"Latitude out of range: {lat}")
        return self


# ───────────────────────────────────────────────────────────────────────
# Operation (S8e)
# ───────────────────────────────────────────────────────────────────────


class OperationAreaIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    area_index: int = Field(ge=1)
    label: str | None = Field(default=None, max_length=120)
    polygon: Polygon


class OperationAreaOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    area_index: int
    label: str | None
    polygon: dict[str, Any]


class OpenOperationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city_label: str = Field(min_length=1, max_length=120)
    areas: list[OperationAreaIn] = Field(min_length=1)
    access_code_active: bool = False
    plausibility_threshold_m: int | None = Field(default=None, ge=50, le=50_000)


class ChangeOperationAreasRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    areas: list[OperationAreaIn] = Field(min_length=1)


class ToggleAccessCodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activate: bool


class SupplyTransporterModeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_id: uuid.UUID
    mode: Literal["off", "mobile_supply", "large_order"]


class OperationOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    tenant_id: uuid.UUID
    status: Literal["planned", "active", "closed"]
    city_label: str
    url_token: str
    access_code_active: bool
    opened_at: datetime | None
    closed_at: datetime | None
    plausibility_threshold_m: int | None
    areas: list[OperationAreaOut]


class AccessCodeIssueOut(BaseModel):
    """Antwort beim Aktivieren des AccessCodes — enthält den Klartext-Code
    **einmalig** zum Ausdrucken / QR-Rendering im Disponenten-UI. Wird
    nicht persistiert (siehe ADR-005)."""

    model_config = ConfigDict(extra="forbid")

    access_code_active: bool
    access_code: str | None


# ───────────────────────────────────────────────────────────────────────
# Orders (S2c + S8e)
# ───────────────────────────────────────────────────────────────────────

_ORDER_ITEM_REGEX_HEX_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


class OrderItemIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_item_id: uuid.UUID | None = None
    tenant_extension_id: uuid.UUID | None = None
    quantity: Annotated[int, Field(gt=0, le=10_000)]

    @model_validator(mode="after")
    def _exactly_one_ref(self) -> OrderItemIn:
        if (self.base_item_id is None) == (self.tenant_extension_id is None):
            raise ValueError("Exactly one of base_item_id or tenant_extension_id must be set")
        return self


class PlaceOrderRequest(BaseModel):
    """Anon-Bestellung (POST /api/anon/{url}/order).

    Entweder GPS oder Text-Standort. ``accuracy_m`` ist optional, fehlt
    sie bei vorhandenem GPS → Plausibility-Outcome
    ``MODERATION_ACCURACY_TOO_LOW``.
    """

    model_config = ConfigDict(extra="forbid")

    items: list[OrderItemIn] = Field(min_length=1, max_length=50)
    location_lat: float | None = Field(default=None, ge=-90.0, le=90.0)
    location_lng: float | None = Field(default=None, ge=-180.0, le=180.0)
    location_accuracy_m: float | None = Field(default=None, gt=0.0, le=10_000.0)
    location_text: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _validate_location(self) -> PlaceOrderRequest:
        has_lat = self.location_lat is not None
        has_lng = self.location_lng is not None
        if has_lat != has_lng:
            raise ValueError("location_lat and location_lng must both be set or both be omitted")
        if not has_lat and not self.location_text:
            raise ValueError(
                "Either GPS (location_lat + location_lng) or location_text is required"
            )
        return self


class OrderItemOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    base_item_id: uuid.UUID | None
    tenant_extension_id: uuid.UUID | None
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    operation_id: uuid.UUID
    anonymous_session_id: uuid.UUID | None
    placed_at: datetime
    status: Literal[
        "pending",
        "needs_moderation",
        "assigned",
        "in_progress",
        "completed",
        "cancelled",
    ]
    location_lat: float | None
    location_lng: float | None
    location_accuracy_m: float | None
    location_text: str | None
    plausibility_outcome: Literal[
        "ACCEPTED",
        "MODERATION_NO_GPS",
        "MODERATION_ACCURACY_TOO_LOW",
        "MODERATION_OUT_OF_RANGE",
    ]
    plausibility_distance_m: float | None
    plausibility_threshold_m: int
    plausibility_variant: str
    moderation_actor_dispatcher_id: uuid.UUID | None
    moderation_at: datetime | None
    items: list[OrderItemOut]


# Anonymes Order-Response — auf das Notwendige reduziert (kein Audit für
# die Einsatzkraft sichtbar; keine Disponenten-IDs).
class AnonymousOrderOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    status: Literal[
        "pending",
        "needs_moderation",
        "assigned",
        "in_progress",
        "completed",
        "cancelled",
    ]
    plausibility_outcome: Literal[
        "ACCEPTED",
        "MODERATION_NO_GPS",
        "MODERATION_ACCURACY_TOO_LOW",
        "MODERATION_OUT_OF_RANGE",
    ]
    placed_at: datetime


class AssignVehicleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_id: uuid.UUID


class OrderAssignmentOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    order_id: uuid.UUID
    vehicle_id: uuid.UUID
    dispatcher_id: uuid.UUID
    status: Literal["assigned", "in_progress", "completed", "cancelled"]
    assigned_at: datetime
    completed_at: datetime | None


# ───────────────────────────────────────────────────────────────────────
# Audit-Log (S8e)
# ───────────────────────────────────────────────────────────────────────


class AuditLogEntryOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    operation_id: uuid.UUID
    actor_dispatcher_id: uuid.UUID | None
    action_type: str
    at: datetime
    target_kind: str
    target_id: uuid.UUID
    payload: dict[str, Any] | None


__all__ = [
    "AccessCodeIssueOut",
    "AnonymousOrderOut",
    "AssignVehicleRequest",
    "AuditLogEntryOut",
    "ChangeOperationAreasRequest",
    "OpenOperationRequest",
    "OperationAreaIn",
    "OperationAreaOut",
    "OperationOut",
    "OrderAssignmentOut",
    "OrderItemIn",
    "OrderItemOut",
    "OrderOut",
    "PlaceOrderRequest",
    "Polygon",
    "SupplyTransporterModeRequest",
    "ToggleAccessCodeRequest",
]
