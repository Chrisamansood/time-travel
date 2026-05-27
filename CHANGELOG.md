# Changelog

All notable changes to Time Travel will be documented here.
This project follows [Semantic Versioning](https://semver.org/).

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
