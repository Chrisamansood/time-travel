"""CLI entry point for time-travel.

All subcommands are stubbed in Plan A. The orchestrator (Plan B) and
renderers (Plan C) will replace the NotImplementedError stubs.
"""
from __future__ import annotations

import argparse
import sys


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="time-travel",
        description=(
            "Multi-agent premortem for plans. "
            "Sends personas to the future, brings back risks."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── run ───────────────────────────────────────────────────────────────────
    run = subparsers.add_parser("run", help="Run a premortem on a plan")
    run.add_argument(
        "source",
        nargs="?",
        default=None,
        help="Plan file path or inline text. Omit for auto-detect.",
    )
    run.add_argument("--provider", default=None, help="LLM provider: anthropic|openai|gemini")
    run.add_argument("--model", default=None, help="Model override (provider-specific name)")
    run.add_argument("--search", default="tavily", help="Web search provider (default: tavily)")
    run.add_argument("--fast", action="store_true", help="Skip parallel dispatch (~20%% cost)")
    run.add_argument("--horizons", default="3mo,6mo,12mo", help="Comma-separated horizon list")
    run.add_argument(
        "--output", default="./time-travel-reports", help="Output directory for artifacts"
    )
    run.add_argument(
        "--for-exec", action="store_true", dest="for_exec", help="Emit exec one-pager"
    )
    run.add_argument(
        "--ai-source", action="store_true", dest="ai_source", help="Flag plan as AI-authored"
    )
    run.add_argument(
        "--no-process-log",
        action="store_true",
        dest="no_process_log",
        help="Skip process log",
    )

    # ── render ────────────────────────────────────────────────────────────────
    render = subparsers.add_parser(
        "render", help="Re-render from a saved JSON report (no LLM calls)"
    )
    render.add_argument("report_json", help="Path to a report JSON file")
    render.add_argument("--output", default="./time-travel-reports", help="Output directory")

    # ── doctor ────────────────────────────────────────────────────────────────
    subparsers.add_parser("doctor", help="Verify env vars, deps, and network connectivity")

    # ── personas ──────────────────────────────────────────────────────────────
    personas = subparsers.add_parser("personas", help="Inspect the built-in persona roster")
    personas_sub = personas.add_subparsers(dest="personas_cmd")
    personas_sub.add_parser("list", help="List all personas with domain tags")

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        raise NotImplementedError(
            "Engine not yet installed. Run Plan B to implement the orchestrator."
        )
    elif args.command == "render":
        raise NotImplementedError(
            "Renderer not yet installed. Run Plan C to implement the renderers."
        )
    elif args.command == "doctor":
        print("doctor: checks not yet implemented (Plan B)")
    elif args.command == "personas":
        if args.personas_cmd == "list":
            print("personas list: not yet implemented (Plan B)")
        else:
            parser.parse_args(["personas", "--help"])


if __name__ == "__main__":
    main()
