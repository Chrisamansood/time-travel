"""Tests for CLI argument parsing.

All subcommands are stubs in Plan A — no engine calls happen here.
"""
from __future__ import annotations
import pytest
from unittest.mock import patch


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
