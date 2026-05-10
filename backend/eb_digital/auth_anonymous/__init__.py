"""Anonymous-Session-Modul für die Einsatzkraft-Bezieher-Seite.

Bewusst getrennt vom angemeldeten ``backend/auth``-Modul: anonyme Sessions
sind mandantenneutral, ohne Identitäts-PII (Vision-Constraint), per pro-
Operation neu erzeugter URL erreichbar und optional durch einen AccessCode
geschützt (ADR-005, Regel-006/007).

Phase 2 Schritt 2.3 produktiv: URL-Token via ``itsdangerous.URLSafeSerializer``,
AccessCode-Validierung mit Argon2id-Konstantzeit-Vergleich, anonymous_session-
Tabelle mit 24-h-Hard-Cap und ``expires_at``. S2-Sub-Surface (``/info``,
``/session``) belastbar; Order-Endpunkte folgen mit ``backend/operations`` in
Phase 4.
"""
