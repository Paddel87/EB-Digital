"""``backend/catalog`` — Basis-Artikelkatalog plus mandantenspezifische Erweiterung.

Phase 4 Schritt 4.1 (UMSETZUNG, ADR-019/Regel-019). Drei Tabellen:

  • ``catalog_category`` — Kategorien (Plattform-Admin-gepflegt).
  • ``catalog_item_base`` — zentraler Basis-Katalog (Plattform-Admin-gepflegt).
  • ``catalog_item_tenant_extension`` — mandantenspezifische Items
    (Override eines Base-Items **oder** eigenständiges Tenant-Item).

Effektiver Katalog für eine Operation wird über
``use_cases.resolve_catalog_for_operation(operation_id)`` aufgelöst —
LEFT JOIN über S10/Regel-014, Override-Felder priorisiert.
"""
