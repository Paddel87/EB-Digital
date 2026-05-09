"""Phase-1-Test-Job zur Validierung des Worker-Setups.

Liefert ``"pong"`` und schreibt eine Log-Zeile, sobald der Worker den Job
ausführt. Wird in Phase 2 entfernt, sobald produktive Jobs existieren.
"""

from __future__ import annotations

import logging

from eb_digital.jobs import procrastinate_app

logger = logging.getLogger(__name__)


@procrastinate_app.task(name="ping")
async def ping() -> str:
    logger.info("ping_task_executed", extra={"event": "ping"})
    return "pong"
