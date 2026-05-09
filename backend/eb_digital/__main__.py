"""Command-line entry point: ``python -m eb_digital``.

Subcommands:
  serve   — start the HTTP server (Schritt 1.3).
  worker  — start the Procrastinate background worker (Schritt 1.5).
  admin   — platform-administrator CLI (Schritt 1.6, stub here).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING

from eb_digital import __version__

if TYPE_CHECKING:
    from collections.abc import Callable


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eb_digital",
        description="EB Digital backend command-line interface.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True, metavar="{serve,admin,worker}")

    serve = sub.add_parser("serve", help="Start the HTTP server.")
    # S104: 0.0.0.0 is the intended default for container-internal binding;
    # Caddy reverse-proxy fronts it (project-context.md Abschnitt 8).
    serve.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0).")  # noqa: S104  # nosec B104
    serve.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000).")
    serve.add_argument(
        "--reload",
        action="store_true",
        help="Reload on source changes (development only).",
    )

    admin = sub.add_parser("admin", help="Platform-administrator CLI (Schritt 1.6).")
    admin.add_subparsers(dest="admin_command", metavar="{create,...}")

    worker = sub.add_parser("worker", help="Procrastinate background worker.")
    worker.add_argument(
        "--queue",
        action="append",
        dest="queues",
        default=None,
        help="Queue name to consume (repeatable). Default: all registered queues.",
    )
    worker.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Concurrent in-flight tasks per worker (default: 1).",
    )

    return parser


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from eb_digital.logging import configure_logging
    from eb_digital.settings import get_settings

    # Configure JSON logging up front so that uvicorn's own loggers
    # (uvicorn, uvicorn.access, uvicorn.error) inherit our root handler
    # via propagation when we pass log_config=None.
    configure_logging(get_settings().log_level)
    uvicorn.run(
        "eb_digital.app:create_app",
        factory=True,
        host=str(args.host),
        port=int(args.port),
        reload=bool(args.reload),
        log_config=None,
    )
    return 0


def _cmd_admin(_args: argparse.Namespace) -> int:
    sys.stderr.write(
        "TODO(fahrplan-ref: 1.6): admin CLI is implemented in Phase 1 step 1.6.\n",
    )
    return 2


async def _run_worker(queues: list[str] | None, concurrency: int) -> None:
    from eb_digital.jobs import procrastinate_app

    # Procrastinate's WorkerOptions TypedDict types ``queues`` as ``Iterable[str]``
    # without ``Optional``, but the documented behaviour for ``None`` (= consume
    # every registered queue) is what we want here. We pass the kwarg only when
    # the caller asked for specific queues.
    worker_kwargs: dict[str, object] = {"concurrency": concurrency}
    if queues is not None:
        worker_kwargs["queues"] = queues
    async with procrastinate_app.open_async():
        await procrastinate_app.run_worker_async(**worker_kwargs)  # type: ignore[arg-type]


def _cmd_worker(args: argparse.Namespace) -> int:
    from eb_digital.logging import configure_logging
    from eb_digital.settings import get_settings

    # Configure JSON logging up front so Procrastinate's own loggers
    # (procrastinate.*) inherit the root handler via propagation.
    configure_logging(get_settings().log_level)

    queues: list[str] | None = list(args.queues) if args.queues else None
    concurrency = int(args.concurrency)
    try:
        asyncio.run(_run_worker(queues=queues, concurrency=concurrency))
    except KeyboardInterrupt:
        # Procrastinate handles SIGINT/SIGTERM internally and stops the worker
        # loop cleanly. KeyboardInterrupt at the asyncio layer means a clean
        # shutdown — exit 0.
        return 0
    return 0


_HANDLERS: dict[str, Callable[[argparse.Namespace], int]] = {
    "serve": _cmd_serve,
    "admin": _cmd_admin,
    "worker": _cmd_worker,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return _HANDLERS[str(args.command)](args)


if __name__ == "__main__":
    raise SystemExit(main())
