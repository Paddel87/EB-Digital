"""add anonymous_session and widen operation url_token

Phase 2 Schritt 2.3: ``anonymous_session``-Tabelle für die anonyme
Einsatzkraft-Bezieher-Seite (ADR-005, Regel-006/007). Bewusste Trennung von
``backend/auth`` und kein Tenant-FK — die Bezieher-Seite ist mandantenneutral.

Zusätzlich Spalten-Widening ``operation.url_token`` von ``String(64)`` auf
``String(255)``: ``itsdangerous.URLSafeSerializer``-signierte Tokens sind ca.
80 Zeichen lang (Payload + Signatur). In Schritt 2.1 wurde die Spalte ohne
diesen Hintergrund auf 64 dimensioniert; additive Anpassung ohne Datenverlust.

Diese Migration wurde hand-geschrieben (kein Autogenerate), weil im
sandbox-Worktree kein Docker für eine laufende Postgres-Instanz verfügbar
ist. Verifikation erfolgt im Compose-Smoke-Test (``scripts/dev-smoke.sh``)
über ``alembic upgrade head`` gegen die ``db-init``-Routine.

Revision ID: f14e7ecace66
Revises: c1465f544fd0
Create Date: 2026-05-11 00:00:00+00:00

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f14e7ecace66"
down_revision: str | None = "c1465f544fd0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── operation.url_token: String(64) → String(255) ────────────────────────
    # itsdangerous-signierte Tokens (URLSafeSerializer mit UUID-Payload) sind
    # typischerweise 80-100 Zeichen. Additive Verbreiterung, kein Datenverlust.
    op.alter_column(
        "operation",
        "url_token",
        existing_type=sa.String(length=64),
        type_=sa.String(length=255),
        existing_nullable=False,
    )

    # ── anonymous_session ────────────────────────────────────────────────────
    op.create_table(
        "anonymous_session",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("operation_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["operation.id"],
            name=op.f("fk_anonymous_session_operation_id_operation"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anonymous_session")),
    )
    op.create_index(
        "ix_anonymous_session_operation_id",
        "anonymous_session",
        ["operation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_anonymous_session_operation_id", table_name="anonymous_session")
    op.drop_table("anonymous_session")

    # ACHTUNG: Diese Verschmälerung kann Daten kürzen, wenn ``url_token``-Werte
    # über 64 Zeichen lang sind (z. B. itsdangerous-Tokens aus Schritt 2.3).
    # In Praxis nur sinnvoll, wenn die Datenbank vor 2.3 wiederhergestellt
    # werden soll und entsprechende Operationen vorher abgeschnitten wurden.
    op.alter_column(
        "operation",
        "url_token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=64),
        existing_nullable=False,
    )
