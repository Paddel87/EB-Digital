"""``backend/fleet`` — Fahrzeuge, Beladung, Versorgungs-Transporter-Modi, Geschäftsstelle.

Phase 4 Schritt 4.2 (UMSETZUNG, ADR-019/Regel-019). Fünf Tabellen:

  • ``vehicle`` — Fahrzeug-Stammdaten mit Mandanten-Bindung, Typ-Spalte
    (``regular`` / ``supply_transporter``) und optionalem Modus-Feld
    (nur Supply-Transporter, ``off`` / ``mobile_supply`` / ``large_order``).
  • ``tenant_head_office`` — 1:1-Geschäftsstelle pro Mandant (Lat/Lng/Label).
  • ``vehicle_loadout`` — aktueller Beladungs-Snapshot pro Fahrzeug
    (UNIQUE auf ``vehicle_id``).
  • ``vehicle_loadout_item`` — Beladungs-Positionen, referenzieren entweder
    ein ``catalog_item_base`` ODER ein ``catalog_item_tenant_extension``
    (CHECK exklusiv eine NOT NULL).
  • ``vehicle_loadout_history`` — append-only Frozen-Snapshots vergangener
    Beladungen als JSONB; bei jedem Loadout-Replace befüllt.

Versorgungs-Transporter-Modus-Wechsel läuft in Phase 4.2 ohne Audit-Log
(Detail-Plan 3B); ADR-008/Regel-011-Audit-Pflicht wird in Phase 4.3
durch ``backend/operations.SwitchSupplyTransporterMode``-Umhüllung erfüllt.

S4 (``fleet.assign_vehicle``) und automatische Verbrauchsbuchung gehören
zu Phase 4.3 und sind hier nicht implementiert (Detail-Plan 0A).
"""
