"""add procrastinate schema

Revision ID: 1e343dae5fc4
Revises: 660e1a12a41a
Create Date: 2026-05-09 19:30:00.000000+00:00

Spielt das von ``procrastinate.schema.SchemaManager.get_schema()`` gelieferte
SQL ein. Erzeugt die Tabellen ``procrastinate_workers``, ``procrastinate_jobs``,
``procrastinate_periodic_defers``, ``procrastinate_events``, drei Enum-Typen
und alle Funktionen, Trigger und Indizes der Job-Engine.

asyncpg kann keine Multi-Statement-DDL über prepared statements ausführen
(``cannot insert multiple commands into a prepared statement``). Procrastinate
liefert das Schema aber als einen mehrstatement-SQL-Text. Wir splitten den Text
hier auf Top-Level-Semikolons und respektieren PostgreSQL-Dollar-Quoting
(``$$`` und ``$tag$``), damit Funktionsbodies und der ``DO $$ … $$``-Block
intakt bleiben.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from procrastinate.schema import SchemaManager

revision: str = "1e343dae5fc4"
down_revision: str | None = "660e1a12a41a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _split_postgres_statements(sql: str) -> list[str]:
    """Split einen PostgreSQL-Mehrstatement-Text an Top-Level-Semikolons.

    Respektiert Dollar-Quoting (``$$ … $$`` und ``$tag$ … $tag$``) — innerhalb
    eines dollar-gequoteten Bereichs werden Semikolons ignoriert.
    """
    statements: list[str] = []
    buf: list[str] = []
    in_dollar = False
    dollar_tag = ""
    i = 0
    n = len(sql)
    while i < n:
        if not in_dollar and sql[i] == "$":
            # Suche das passende $-Ende, prüfe ob dazwischen ein gültiger Tag steht.
            end = sql.find("$", i + 1)
            if end != -1:
                inner = sql[i + 1 : end]
                if all(ch.isalnum() or ch == "_" for ch in inner):
                    tag = sql[i : end + 1]
                    in_dollar = True
                    dollar_tag = tag
                    buf.append(tag)
                    i = end + 1
                    continue
            buf.append(sql[i])
            i += 1
            continue
        if in_dollar:
            if sql.startswith(dollar_tag, i):
                buf.append(dollar_tag)
                i += len(dollar_tag)
                in_dollar = False
                dollar_tag = ""
                continue
            buf.append(sql[i])
            i += 1
            continue
        if sql[i] == ";":
            stmt = "".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []
            i += 1
            continue
        buf.append(sql[i])
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def upgrade() -> None:
    for statement in _split_postgres_statements(SchemaManager.get_schema()):
        op.execute(statement)


def downgrade() -> None:
    # Reihenfolge: Tabellen mit CASCADE räumen Trigger und Indizes mit weg.
    # Anschließend Funktionen und Composite-/Enum-Typen explizit löschen.
    # Statements einzeln, weil asyncpg Multi-Statement im prepared-statement-
    # Modus ablehnt (siehe Anmerkung am Datei-Anfang).
    drop_statements = [
        "DROP TABLE IF EXISTS procrastinate_events CASCADE",
        "DROP TABLE IF EXISTS procrastinate_periodic_defers CASCADE",
        "DROP TABLE IF EXISTS procrastinate_jobs CASCADE",
        "DROP TABLE IF EXISTS procrastinate_workers CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_defer_jobs_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_defer_periodic_job_v2 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_fetch_job_v2 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_finish_job_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_cancel_job_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_retry_job_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_retry_job_v2 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_notify_queue_job_inserted_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_notify_queue_abort_job_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_trigger_function_status_events_insert_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_trigger_function_status_events_update_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_trigger_function_scheduled_events_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_trigger_abort_requested_events_procedure_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_unlink_periodic_defers_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_register_worker_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_unregister_worker_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_update_heartbeat_v1 CASCADE",
        "DROP FUNCTION IF EXISTS procrastinate_prune_stalled_workers_v1 CASCADE",
        "DROP TYPE IF EXISTS procrastinate_job_to_defer_v1 CASCADE",
        "DROP TYPE IF EXISTS procrastinate_job_event_type CASCADE",
        "DROP TYPE IF EXISTS procrastinate_job_status CASCADE",
    ]
    for statement in drop_statements:
        op.execute(statement)
