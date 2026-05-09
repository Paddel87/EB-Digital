"""Tests for the python -m eb_digital command-line entry point."""

from __future__ import annotations

import argparse

import pytest

from eb_digital.__main__ import _build_parser, main


def test_parser_requires_a_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])
    err = capsys.readouterr().err
    assert "command" in err.lower() or "required" in err.lower()


def test_serve_subcommand_parses_host_and_port_defaults() -> None:
    parser = _build_parser()
    args = parser.parse_args(["serve"])
    assert args.command == "serve"
    assert args.host == "0.0.0.0"  # noqa: S104  # asserts the intended default
    assert args.port == 8000
    assert args.reload is False


def test_serve_subcommand_accepts_explicit_host_and_port() -> None:
    parser = _build_parser()
    args = parser.parse_args(["serve", "--host", "127.0.0.1", "--port", "9000", "--reload"])
    assert args.host == "127.0.0.1"
    assert args.port == 9000
    assert args.reload is True


def test_admin_subcommand_requires_a_subsubcommand(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # argparse with ``required=True`` on the admin subparser rejects a bare
    # ``admin`` invocation with exit code 2 (argparse default for parse error).
    with pytest.raises(SystemExit) as exc_info:
        _build_parser().parse_args(["admin"])
    assert exc_info.value.code == 2
    err = capsys.readouterr().err
    assert "admin" in err.lower() or "required" in err.lower()


def test_admin_create_subcommand_requires_username(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        _build_parser().parse_args(["admin", "create"])
    assert exc_info.value.code == 2
    err = capsys.readouterr().err
    assert "--username" in err


def test_admin_create_subcommand_parses_username() -> None:
    args = _build_parser().parse_args(["admin", "create", "--username", "patrick"])
    assert args.command == "admin"
    assert args.admin_command == "create"
    assert args.username == "patrick"


def test_admin_create_routes_to_cmd_admin_create(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_cmd_admin_create(args: object) -> int:
        captured["args"] = args
        return 0

    monkeypatch.setattr("eb_digital.auth.cli.cmd_admin_create", fake_cmd_admin_create)
    assert main(["admin", "create", "--username", "patrick"]) == 0
    args = captured["args"]
    assert isinstance(args, argparse.Namespace)
    assert args.username == "patrick"
    assert args.admin_command == "create"


def test_worker_subcommand_parses_default_args() -> None:
    parser = _build_parser()
    args = parser.parse_args(["worker"])
    assert args.command == "worker"
    assert args.queues is None
    assert args.concurrency == 1


def test_worker_subcommand_accepts_repeated_queue_and_concurrency() -> None:
    parser = _build_parser()
    args = parser.parse_args(
        ["worker", "--queue", "default", "--queue", "exports", "--concurrency", "4"]
    )
    assert args.queues == ["default", "exports"]
    assert args.concurrency == 4


def test_worker_subcommand_invokes_run_worker_with_parsed_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    async def fake_run_worker(*, queues: list[str] | None, concurrency: int) -> None:
        captured["queues"] = queues
        captured["concurrency"] = concurrency

    monkeypatch.setattr("eb_digital.__main__._run_worker", fake_run_worker)
    code = main(["worker", "--queue", "default", "--concurrency", "3"])
    assert code == 0
    assert captured == {"queues": ["default"], "concurrency": 3}


def test_worker_subcommand_returns_zero_on_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def raising_run_worker(*, queues: list[str] | None, concurrency: int) -> None:
        del queues, concurrency
        raise KeyboardInterrupt

    monkeypatch.setattr("eb_digital.__main__._run_worker", raising_run_worker)
    assert main(["worker"]) == 0
