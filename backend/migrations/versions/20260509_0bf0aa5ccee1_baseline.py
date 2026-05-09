"""baseline

Revision ID: 0bf0aa5ccee1
Revises:
Create Date: 2026-05-09

Empty baseline migration. Real schema arrives in Phase 2 (auth, tenants).
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0bf0aa5ccee1"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
