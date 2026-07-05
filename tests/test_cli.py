"""Tests for CLI argument parsing and command wiring."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from time_travel.models import Rebuttal, Report, UserPOV


def get_parser():
    from time_travel.cli import create_parser
    return create_parser()


# ── run command ─────────────────────────────────────────────────────────────────

def test_run_no_source_sets_source_none():
    args = get_parser().parse_args(["run"])
    assert args.command == "run"
    assert args.source is None


def test_run_with_file_path():
    args = get_parser().parse_args(["run", "my-plan.md"])
    assert args.source == "my-plan.md"


def test_run_provider_flag():
    args = get_parser().parse_args(["run", "--provider", "openai"])
    assert args.provider == "openai"


def test_run_provider_defaults_to_none():
    args = get_parser().parse_args(["run"])
    assert args.provider is None


def test_run_model_defaults_to_none():
    args = get_parser().parse_args(["run"])
    assert args.model is None


def test_run_search_default():
    args = get_parser().parse_args(["run"])
    assert args.search == "tavily"


def test_run_fast_flag():
    args = get_parser().parse_args(["run", "--fast"])
    assert args.fast is True


def test_run_fast_default_false():
    args = get_parser().parse_args(["run"])
    assert args.fast is False


def test_run_horizons_default():
    args = get_parser().parse_args(["run"])
    assert args.horizons == "3mo,6mo,12mo"


def test_run_horizons_override():
    args = get_parser().parse_args(["run", "--horizons", "1mo,3mo,1y"])
    assert args.horizons == "1mo,3mo,1y"


def test_run_output_default():
    args = get_parser().parse_args(["run"])
    assert args.output == "./time-travel-reports"


def test_run_output_override():
    args = get_parser().parse_args(["run", "--output", "/tmp/reports"])
    assert args.output == "/tmp/reports"


def test_run_for_exec_flag():
    args = get_parser().parse_args(["run", "--for-exec"])
    assert args.for_exec is True


def test_run_ai_source_flag():
    args = get_parser().parse_args(["run", "--ai-source"])
    assert args.ai_source is True


def test_run_no_process_log_flag():
    args = get_parser().parse_args(["run", "--no-process-log"])
    assert args.no_process_log is True


def test_run_combined_flags():
    args = get_parser().parse_args([
        "run", "plan.md",
        "--provider", "anthropic",
        "--model", "claude-opus-4-5",
        "--fast",
        "--for-exec",
        "--output", "/tmp/out",
    ])
    assert args.source == "plan.md"
    assert args.provider == "anthropic"
    assert args.model == "claude-opus-4-5"
    assert args.fast is True
    assert args.for_exec is True
    assert args.output == "/tmp/out"


# ── render command ───────────────────────────────────────────────────────────────

def test_render_requires_json_path():
    args = get_parser().parse_args(["render", "report.json"])
    assert args.command == "render"
    assert args.report_json == "report.json"


def test_render_output_default():
    args = get_parser().parse_args(["render", "report.json"])
    assert args.output == "./time-travel-reports"


# ── doctor command ───────────────────────────────────────────────────────────────

def test_doctor_command_parses():
    args = get_parser().parse_args(["doctor"])
    assert args.command == "doctor"


# ── personas command ─────────────────────────────────────────────────────────────

def test_personas_list_parses():
    args = get_parser().parse_args(["personas", "list"])
    assert args.command == "personas"
    assert args.personas_cmd == "list"


# ── no command exits with code 1 ─────────────────────────────────────────────────

def test_no_command_exits_with_code_1():
    with patch("sys.argv", ["time-travel"]):
        with pytest.raises(SystemExit) as exc:
            from time_travel.cli import main
            main()
    assert exc.value.code == 1


# ── run command wiring (Plan B7) ──────────────────────────────────────────────────

def _fake_report():
    return Report(
        plan_title="Test Plan",
        plan_source="plan.md",
        generated_at=datetime(2026, 1, 1),
        horizons=["3mo", "6mo", "12mo"],
        plan_text="text",
        user_pov=UserPOV("", "", "", ""),
        personas=[],
        narratives={},
        confirmed_risks=[],
        inflated_risks=[],
        buried_risks=[],
        rebuttal=Rebuttal([], [], []),
        mitigations=[],
        revised_plan="text",
        evidence=[],
        unmitigated_confidence=100,
        mitigated_confidence=100,
        report_id="20260101T000000",
    )


def test_run_command_calls_orchestrator_with_parsed_options(monkeypatch):
    from time_travel import cli

    captured = {}

    async def fake_run(source, opts, **kwargs):
        captured["source"] = source
        captured["opts"] = opts
        return _fake_report()

    monkeypatch.setattr(cli.orchestrator, "run", fake_run)

    with patch("sys.argv", ["time-travel", "run", "plan.md", "--for-exec", "--provider", "stub"]):
        cli.main()

    assert captured["source"] == "plan.md"
    assert captured["opts"].for_exec is True
    assert captured["opts"].provider == "stub"


def test_run_command_does_not_raise_not_implemented(monkeypatch):
    from time_travel import cli

    async def fake_run(source, opts, **kwargs):
        return _fake_report()

    monkeypatch.setattr(cli.orchestrator, "run", fake_run)

    with patch("sys.argv", ["time-travel", "run", "plan.md"]):
        cli.main()  # must not raise


# ── render command wiring (Plan B7) ───────────────────────────────────────────────

def test_render_command_calls_orchestrator_render_from_json(monkeypatch, tmp_path):
    from time_travel import cli

    captured = {}

    def fake_render_from_json(report_json_path, output_dir):
        captured["report_json_path"] = report_json_path
        captured["output_dir"] = output_dir
        return tmp_path / "rendered"

    monkeypatch.setattr(cli.orchestrator, "render_from_json", fake_render_from_json)

    with patch(
        "sys.argv", ["time-travel", "render", "report.json", "--output", str(tmp_path)]
    ):
        cli.main()

    assert captured["report_json_path"] == "report.json"
    assert captured["output_dir"] == str(tmp_path)
