"""Operations module: Lebenszyklus von Operations + Audit-Log.

Phase 2 Schritt 2.1 enthält nur das Datenmodell-Skelett (``Operation``
ohne direkte Tenant-FK gemäß I1, ``OperationAuditLog`` als Strukturskelett
gemäß ADR-008). Use-Case-Logik (Eröffnen/Beenden, Bestellungen,
Fahrzeug-Zuweisung, Stornierung, Bündelung, Audit-Log-Schreibung) folgt in
Phase 4.
"""
