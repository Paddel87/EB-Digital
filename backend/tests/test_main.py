"""Tests for the python -m eb_digital command-line entry point."""

from __future__ import annotations

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


def test_admin_subcommand_is_a_stub_with_exit_code_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = main(["admin"])
    assert code == 2
    assert "1.6" in capsys.readouterr().err


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
