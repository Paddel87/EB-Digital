"""Procrastinate-App-Setup für EB Digital.

Job-Engine ist Procrastinate (Stack-fix per ADR-002, LGPL-Sub-Dep ``psycopg``
explizit per ADR-011 akzeptiert). Connector ist ``PsycopgConnector`` — der
Procrastinate-Default-Pfad mit ACID-Job-State direkt in PostgreSQL, läuft mit
einem eigenen psycopg3-Pool getrennt vom asyncpg/SQLAlchemy-Pool des ORM.

Job-Modul-Konvention: jedes Backend-Modul mit Hintergrund-Jobs hat ein
Submodul ``jobs/`` mit registrierten Tasks. In Phase 1 enthält ``jobs/``
nur den ``ping``-Test-Job; produktive Tasks (Datenexport, Retention,
Aggregat-Berechnung) folgen ab Phase 2.
"""

from __future__ import annotations

from procrastinate import App, PsycopgConnector

from eb_digital.settings import get_settings


def _to_psycopg_conninfo(database_url: str) -> str:
    """Wandle eine SQLAlchemy-URL (``postgresql+asyncpg://…``) in ein für
    psycopg3 verstehbares ``postgresql://``-Format um."""
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


def make_procrastinate_app() -> App:
    """Erzeuge eine Procrastinate-App-Instance gegen die aktuelle DB-URL.

    Tests und CLI-Aufrufe verwenden diese Factory, damit eine Settings-
    Manipulation (z. B. anderer DB-Pfad) konsistent durchschlägt.
    """
    settings = get_settings()
    return App(
        connector=PsycopgConnector(conninfo=_to_psycopg_conninfo(settings.database_url)),
    )


# Modul-Level-Default-App. Nutzung: ``from eb_digital.jobs import procrastinate_app``.
procrastinate_app: App = make_procrastinate_app()

# Submodule mit ``@procrastinate_app.task``-Registrierungen importieren.
# Side-Effekt-Import nach Definition von ``procrastinate_app`` ist Absicht.
from eb_digital.jobs import ping  # noqa: E402, F401

__all__ = ["make_procrastinate_app", "procrastinate_app"]
