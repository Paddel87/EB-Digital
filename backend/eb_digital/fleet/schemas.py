"""Pydantic-v2-Schemas für ``backend/fleet``.

Trennt Eingabe (``*Create``/``*Update``-Suffix) von Ausgabe (``*Out``-
Suffix). Range-Validierung auf Lat/Lng dupliziert die DB-CHECK als
benutzerfreundlicher Frühabbruch (422 statt 500).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eb_digital.fleet.models import (
    ALLOWED_SUPPLY_MODES,
    ALLOWED_VEHICLE_TYPES,
)

# Vehicle ----------------------------------------------------------------


class VehicleCreate(BaseModel):
    """Eingabe für ``POST /api/fleet/vehicles`` (Disponent eigener Tenant)."""

    type: Annotated[str, Field(min_length=1, max_length=32)]
    name: Annotated[str, Field(min_length=1, max_length=120)]
    license_plate: Annotated[str | None, Field(default=None, max_length=32)] = None
    capacity_label: Annotated[str | None, Field(default=None, max_length=64)] = None

    @model_validator(mode="after")
    def _check_type(self) -> VehicleCreate:
        if self.type not in ALLOWED_VEHICLE_TYPES:
            raise ValueError("type muss 'regular' oder 'supply_transporter' sein")
        return self


class VehicleUpdate(BaseModel):
    """Partial-Update für ``PATCH /api/fleet/vehicles/{id}``.

    Typ-Wechsel ist verboten — eine Änderung von ``type`` wird im Use-Case
    abgelehnt; das Schema lässt sie aus, um Missverständnisse zu vermeiden.
    """

    name: Annotated[str | None, Field(default=None, min_length=1, max_length=120)] = None
    license_plate: Annotated[str | None, Field(default=None, max_length=32)] = None
    capacity_label: Annotated[str | None, Field(default=None, max_length=64)] = None


class VehicleModeUpdate(BaseModel):
    """Eingabe für ``POST /api/fleet/vehicles/{id}/mode``."""

    mode: Annotated[str, Field(min_length=1, max_length=32)]

    @model_validator(mode="after")
    def _check_mode(self) -> VehicleModeUpdate:
        if self.mode not in ALLOWED_SUPPLY_MODES:
            raise ValueError("mode muss 'off', 'mobile_supply' oder 'large_order' sein")
        return self


class VehicleOut(BaseModel):
    """Ausgabe-Schema für ``Vehicle``."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    type: str
    mode: str | None
    name: str
    license_plate: str | None
    capacity_label: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# HeadOffice ------------------------------------------------------------


class HeadOfficeUpsert(BaseModel):
    """Eingabe für ``PUT /api/fleet/head-office`` (oder Disponent eigener Tenant).

    Lat/Lng-Range dupliziert die DB-CHECK als 422-Frühabbruch.
    """

    lat: Annotated[float, Field(ge=-90.0, le=90.0)]
    lng: Annotated[float, Field(ge=-180.0, le=180.0)]
    label: Annotated[str | None, Field(default=None, max_length=120)] = None


class HeadOfficeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: uuid.UUID
    lat: float
    lng: float
    label: str | None
    created_at: datetime
    updated_at: datetime


# Loadout ---------------------------------------------------------------


class LoadoutItemInput(BaseModel):
    """Eine Position der Beladung in ``PUT /api/fleet/vehicles/{id}/loadout``.

    Genau eine der beiden Ref-Spalten muss gesetzt sein — dasselbe Modell
    wie der DB-CHECK ``exactly_one_ref``. Schema-Validierung gibt 422
    statt der DB-Fehlermeldung.
    """

    base_item_id: uuid.UUID | None = None
    tenant_extension_id: uuid.UUID | None = None
    quantity: Annotated[int, Field(ge=1)]

    @model_validator(mode="after")
    def _check_exactly_one_ref(self) -> LoadoutItemInput:
        has_base = self.base_item_id is not None
        has_ext = self.tenant_extension_id is not None
        if has_base == has_ext:
            raise ValueError(
                "genau eine von base_item_id und tenant_extension_id muss gesetzt sein"
            )
        return self


class LoadoutUpsert(BaseModel):
    """Komplette Beladung des Fahrzeugs atomar setzen.

    Leere Liste = Fahrzeug leer (kein Item). Der Use-Case ersetzt den
    Snapshot atomar; der vorherige Stand landet in
    ``vehicle_loadout_history``.
    """

    items: list[LoadoutItemInput]


class LoadoutItemOut(BaseModel):
    """Ein Item-Eintrag in der Loadout-Antwort."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    base_item_id: uuid.UUID | None
    tenant_extension_id: uuid.UUID | None
    quantity: int


class LoadoutOut(BaseModel):
    """Ausgabe-Schema für ``vehicle_loadout`` mit eingebetteten Items."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    recorded_at: datetime
    recorded_by_dispatcher_id: uuid.UUID
    items: list[LoadoutItemOut]


class LoadoutHistoryEntryOut(BaseModel):
    """Ein Eintrag der Loadout-History (Frozen JSONB items)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    recorded_at: datetime
    recorded_by_dispatcher_id: uuid.UUID
    items: list[dict[str, str | int]]


class LoadoutHistoryOut(BaseModel):
    """Paginierte Antwort für ``GET /loadout/history``."""

    entries: list[LoadoutHistoryEntryOut]


# Fehler-Tag (für Discriminator-Use im Mapping; primäre Quelle bleiben
# die Use-Case-Exceptions, dieses Modul liefert nur Typen.) --------------

VehicleTypeLiteral = Literal["regular", "supply_transporter"]
SupplyModeLiteral = Literal["off", "mobile_supply", "large_order"]


__all__ = [
    "HeadOfficeOut",
    "HeadOfficeUpsert",
    "LoadoutHistoryEntryOut",
    "LoadoutHistoryOut",
    "LoadoutItemInput",
    "LoadoutItemOut",
    "LoadoutOut",
    "LoadoutUpsert",
    "SupplyModeLiteral",
    "VehicleCreate",
    "VehicleModeUpdate",
    "VehicleOut",
    "VehicleTypeLiteral",
    "VehicleUpdate",
]
