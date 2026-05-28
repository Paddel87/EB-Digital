"""Domain-Exceptions für ``backend/operations``.

Mapping auf HTTP-Statuscodes erfolgt im API-Layer (``api.py``). Die
Exceptions selbst sind framework-agnostisch.
"""

from __future__ import annotations


class OperationsError(Exception):
    """Basis aller Operations-Domain-Errors."""


class OperationNotFoundError(OperationsError):
    """404 — Operation existiert nicht oder ist nicht sichtbar."""


class OperationAlreadyClosedError(OperationsError):
    """409 — Operation ist bereits ``closed``."""


class OperationNotActiveError(OperationsError):
    """422 — Operation ist nicht im Status ``active`` (z. B. Bestellungen
    aus geschlossenen oder geplanten Operations sind verboten)."""


class OperationAreaNotFoundError(OperationsError):
    """404 — Einsatzraum (innerhalb einer Operation) existiert nicht."""


class OrderNotFoundError(OperationsError):
    """404 — Bestellung existiert nicht oder gehört zu anderer Operation."""


class OrderNotPendingError(OperationsError):
    """409 — Aktion verlangt Order-Status ``pending`` (Disponent zuweisen,
    stornieren). Order war bereits in einem anderen Status."""


class OrderNotInModerationError(OperationsError):
    """409 — Approve-Aktion verlangt Order-Status ``needs_moderation``."""


class OrderNotAssignedError(OperationsError):
    """409 — Aktion verlangt Order-Status ``assigned`` oder
    ``in_progress`` (Complete)."""


class OrderAlreadyAssignedError(OperationsError):
    """409 — Order hat bereits ein aktives Assignment."""


class VehicleNotEligibleError(OperationsError):
    """422 — Fahrzeug-Tenant nimmt nicht am Einsatz teil (Invariante I3 /
    Regel-014)."""


class VehicleNotFoundError(OperationsError):
    """404 — Fahrzeug existiert nicht oder ist nicht sichtbar."""


class NotParticipantError(OperationsError):
    """403 — Akteur (Dispatcher) nimmt nicht am Einsatz teil
    (Regel-014). Auch verwendet, wenn der zugreifende Mandant keinen
    Owner-Eintrag in ``operation_tenant_participation`` hat."""


class CarerNotEligibleError(OperationsError):
    """403 — Carer gehört zu einem nicht teilnehmenden Mandanten."""


class AnonymousSessionInvalidError(OperationsError):
    """401 — anonyme Session ist abgelaufen oder existiert nicht."""


class AnonymousSessionOperationMismatchError(OperationsError):
    """401 — anonyme Session gehört nicht zur referenzierten Operation."""


class CatalogItemNotAvailableError(OperationsError):
    """422 — Catalog-Item ist deaktiviert (Base ``is_active=False`` oder
    Tenant-Extension ``is_disabled=True``)."""


class CrossTenantExtensionError(OperationsError):
    """422 — Tenant-Extension gehört zu einem fremden Mandanten."""


class EmptyOrderError(OperationsError):
    """422 — Bestellung ohne Items."""


class InvalidPolygonError(OperationsError):
    """422 — Polygon-JSON ist kein gültiges GeoJSON-Polygon."""


class InvalidLocationError(OperationsError):
    """422 — Location-Felder verletzen die Konsistenz (z. B. lat ohne lng,
    weder GPS noch Text)."""


__all__ = [
    "AnonymousSessionInvalidError",
    "AnonymousSessionOperationMismatchError",
    "CarerNotEligibleError",
    "CatalogItemNotAvailableError",
    "CrossTenantExtensionError",
    "EmptyOrderError",
    "InvalidLocationError",
    "InvalidPolygonError",
    "NotParticipantError",
    "OperationAlreadyClosedError",
    "OperationAreaNotFoundError",
    "OperationNotActiveError",
    "OperationNotFoundError",
    "OperationsError",
    "OrderAlreadyAssignedError",
    "OrderNotAssignedError",
    "OrderNotFoundError",
    "OrderNotInModerationError",
    "OrderNotPendingError",
    "VehicleNotEligibleError",
    "VehicleNotFoundError",
]
