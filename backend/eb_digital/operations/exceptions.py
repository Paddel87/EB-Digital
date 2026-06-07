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


# ─── Bündelung (Schritt 4.3b, ADR-018) ───────────────────────────────────


class MinimumTwoOrdersError(OperationsError):
    """422 — Bündel braucht mindestens 2 Orders (ADR-018 B6)."""


class EmptyBundleError(OperationsError):
    """422 — Bündel mit leerer Order-Liste (ADR-018 B7)."""


class VehicleNotInLargeOrderModeError(OperationsError):
    """422 — Versorgungs-Transporter, aber ``mode != 'large_order'``
    (ADR-018 B2)."""


class OrderNotInOperationError(OperationsError):
    """422 — Order gehört zu einer anderen Operation als der Bündel-
    Operation (ADR-018 B5)."""


class OrderAlreadyBundledError(OperationsError):
    """422 — Order ist bereits Teil eines Bündels (``bundle_id IS NOT NULL``,
    ADR-018 B4)."""


class OrderInActiveBundleError(OperationsError):
    """409 — Einzel-Order-Storno in einem aktiven Bündel ist Phase 1 nicht
    erlaubt (Detail-Plan 4.3b-3A / ADR-018 §705). Bündel zuerst auflösen
    (``DissolveBundle``)."""


class BundleNotFoundError(OperationsError):
    """404 — Bündel existiert nicht oder gehört zu anderer Operation."""


class BundleNotActiveError(OperationsError):
    """409 — Aktion (Auflösen) verlangt Bündel-Status ``active``."""


__all__ = [
    "AnonymousSessionInvalidError",
    "AnonymousSessionOperationMismatchError",
    "BundleNotActiveError",
    "BundleNotFoundError",
    "CarerNotEligibleError",
    "CatalogItemNotAvailableError",
    "CrossTenantExtensionError",
    "EmptyBundleError",
    "EmptyOrderError",
    "InvalidLocationError",
    "InvalidPolygonError",
    "MinimumTwoOrdersError",
    "NotParticipantError",
    "OperationAlreadyClosedError",
    "OperationAreaNotFoundError",
    "OperationNotActiveError",
    "OperationNotFoundError",
    "OperationsError",
    "OrderAlreadyAssignedError",
    "OrderAlreadyBundledError",
    "OrderInActiveBundleError",
    "OrderNotAssignedError",
    "OrderNotFoundError",
    "OrderNotInModerationError",
    "OrderNotInOperationError",
    "OrderNotPendingError",
    "VehicleNotEligibleError",
    "VehicleNotFoundError",
    "VehicleNotInLargeOrderModeError",
]
