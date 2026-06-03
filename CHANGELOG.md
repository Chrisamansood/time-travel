# Changelog

All notable changes to Time Travel will be documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [1.0.0-dev] - 2026-05-28

### Added (Plan A — Foundation)
- Polyglot monorepo layout: `src/time_travel/`, `harnesses/`, `tests/`, `examples/`, `scripts/`
- Canonical `Report` dataclass with all sub-types and JSON round-trip (`models.py`)
- `LLMProvider` ABC defining the `complete` + `complete_parallel` interface (`providers/base.py`)
- Full CLI argument parser with all v1.0 flags: `run`, `render`, `doctor`, `personas list` (`cli.py`)
- Migrated existing Claude Code plugin to `harnesses/claude-code/plugins/time-travel/`
- Added Codex skill stub at `harnesses/codex/skills/time-travel/`
- 40 tests covering model construction, JSON round-trip, provider ABC, and CLI parsing

### Changed
- Moved `plugins/time-travel/` → `harnesses/claude-code/plugins/time-travel/` (content unchanged)
- Fixed `marketplace.json` plugin source path after restructure
- Renamed `Risk.mitigation` → `Risk.mitigation_summary` to avoid naming collision with `Mitigation` class

### Upcoming (Plans B/C/D)
- Plan B: Orchestrator, provider adapters (Anthropic/OpenAI/Gemini), Tavily search, persona library, synthesis
- Plan C: HTML + Markdown renderers
- Plan D: Thin harness SKILL.md wrappers, install script, GitHub Actions CI

## [Unreleased]

### Added
- Initial release scaffold.

## [0.1.0] — TBD

### Added
- Multi-agent premortem skill with adaptive 5–7 persona roster.
- Multi-horizon timeline narratives (T+3mo, T+6mo, T+12mo) per persona.
- Web-search grounding for real-world analogue failure cases.
- Three-bucket risk classification: Confirmed / Inflated / Buried.
- Urgency tiers for Confirmed risks: Block / Patch-fast / Monitor.
- AI-optimism persona triggered by `--ai-source` flag.
- Exec one-pager output mode via `--for-exec` flag (≤300 words).
- "What would change my mind?" evidence column per top risk.
- Tripwire (first-signal) field per top risk.
- Revised-confidence estimate (unmitigated → mitigated).
- Two-artifact output by default: report + process log.
- Single-call `--fast` mode for cheaper runs.
- Configurable horizons via `--horizons` flag.
