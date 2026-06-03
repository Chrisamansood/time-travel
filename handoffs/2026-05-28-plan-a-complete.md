# Handoff: time-travel v1.0 — Plan A Complete

**Date:** 2026-05-28
**Session outcome:** Plan A (Foundation) fully implemented, reviewed, and pushed to GitHub.

---

## What was accomplished

Built the foundational Python package for the time-travel v1.0 cross-harness upgrade. Transformed the existing Claude-Code-only plugin into a polyglot monorepo ready for a provider-agnostic Python engine.

**Repo is live:** https://github.com/Chrisamansood/time-travel

---

## Key decisions made

| Decision | Choice |
|---|---|
| Harness scope | Provider-agnostic: Anthropic + OpenAI + Gemini |
| Report formats | HTML + Markdown, both always generated |
| Engine language | Python ≥3.10 |
| HTML aesthetic | Neutral editorial (OSS-friendly, no personal brand) |
| Repo shape | Polyglot monorepo (src/ + harnesses/ + tests/) |
| Engine model | Python runner is single engine; skill files are thin wrappers that shell out |
| Web search | Tavily only in v1.0 |
| HTML packaging | Single self-contained .html file |
| Font strategy | System fonts only (no web fonts — keeps HTML self-contained) |

---

## All files created/modified

### New structure
```
time-travel/
├── .claude-plugin/marketplace.json         ← fixed URL to Chrisamansood
├── harnesses/
│   ├── claude-code/plugins/time-travel/    ← migrated from plugins/
│   ├── codex/skills/time-travel/SKILL.md   ← thin wrapper stub
│   └── gemini/README.md                    ← v1.1 placeholder
├── src/time_travel/
│   ├── __init__.py
│   ├── models.py                           ← canonical Report dataclass
│   ├── cli.py                              ← full argparse CLI
│   ├── providers/
│   │   ├── __init__.py
│   │   └── base.py                         ← LLMProvider ABC
│   ├── render/__init__.py
│   ├── search/__init__.py
│   ├── personas/__init__.py
│   └── templates/
├── tests/
│   ├── __init__.py
│   ├── test_models.py                      ← 13 tests
│   ├── test_provider_base.py               ← 6 tests
│   └── test_cli.py                         ← 21 tests
├── examples/sample-plan.md                 ← SaaS MVP fixture
├── pyproject.toml                          ← PEP 621, entry point
├── docs/superpowers/
│   ├── specs/2026-05-26-time-travel-cross-harness-design.md
│   └── plans/2026-05-26-time-travel-v1-plan-a-foundation.md
└── handoffs/2026-05-28-plan-a-complete.md  ← this file
```

### Git log
```
6e17861  fix: update GitHub URLs to correct username (Chrisamansood)
816af1e  chore: Plan A complete — update CHANGELOG, fix lint/types
ba7aee6  feat: add CLI argument parser with all flags
4d6835c  feat: add LLMProvider ABC
0b1ce39  fix: address code review findings on models.py
c6e9b60  feat: add canonical Report data model with JSON round-trip
4b2a4a6  feat: add pyproject.toml and package skeleton
1b4066f  fix: update marketplace.json plugin source path after restructure
3498cfa  chore: restructure into polyglot monorepo layout
f2f9be2  chore: init repo with existing MIT-licensed files
```

---

## Current state

- **40 tests passing** (13 models + 6 provider_base + 21 cli)
- **ruff clean, mypy clean**
- `pip install -e .` works
- `time-travel --help` shows all subcommands
- `time-travel run plan.md` raises `NotImplementedError` (expected — Plan B implements it)

### Key type notes from code review (carried into Plan B)
- `Risk.mitigation_summary` (NOT `Risk.mitigation`) — renamed to avoid clash with `Mitigation` class
- `flags_used: dict[str, bool]` on Report
- `generated_at` on Report uses ISO datetime encoder/decoder — **naive datetimes only** (timezone-aware datetimes not safe on Python <3.11)

---

## Open items / next steps

### Immediate next: Plan B — The Engine

Plan B makes `time-travel run examples/sample-plan.md` actually work. It covers:

1. **`src/time_travel/personas/library.py`** — Convert `references/persona-library.md` into Python dataclasses (PersonaDefinition, domain tags, universal vs domain-specific flags)
2. **`src/time_travel/personas/selection.py`** — Roster picker (2-3 universal + 3-4 domain-specific)
3. **`src/time_travel/search/tavily.py`** + `search/base.py` — WebSearch ABC + Tavily adapter
4. **`src/time_travel/providers/anthropic_provider.py`** — Anthropic adapter with prompt caching, `asyncio.gather` for parallel
5. **`src/time_travel/providers/openai_provider.py`** — OpenAI adapter
6. **`src/time_travel/providers/gemini_provider.py`** — Gemini adapter
7. **`src/time_travel/synthesis.py`** — Deduplicate, classify (Confirmed/Inflated/Buried), confidence math
8. **`src/time_travel/orchestrator.py`** — 6-phase pipeline wiring everything together
9. **Update `src/time_travel/cli.py`** — Wire `run` command to `orchestrator.run()` instead of `NotImplementedError`

**End state of Plan B:** `time-travel run examples/sample-plan.md --provider anthropic` runs the full premortem and writes a `Report` JSON to `./time-travel-reports/`.

### After Plan B: Plan C — Renderers
HTML report + Markdown report both rendered from the Report JSON.

### After Plan C: Plan D — Harnesses + CI
Thin SKILL.md wrappers updated, install script, GitHub Actions.

---

## Gotchas for next session

1. **Working directory has a space:** Always quote it — `"/Users/macbook/Documents/Chris developed Applications /time-travel"`
2. **Venv location:** `.venv/` in the repo root. Always `source .venv/bin/activate` before running Python.
3. **GitHub remote is live:** `git push origin main` works (gh auth was done in user's terminal).
4. **Persona library source:** The existing `references/persona-library.md` is at `harnesses/claude-code/plugins/time-travel/skills/time-travel/references/persona-library.md` — Plan B should convert it to Python, not rewrite it from scratch.
5. **The spec is at:** `docs/superpowers/specs/2026-05-26-time-travel-cross-harness-design.md` — Plan B implementer should read §4 (architecture) and §6 (provider adapters) before starting.
6. **Plan B plan file:** Does not exist yet — next session should write it first using `superpowers:writing-plans` before executing.

---

## How to restart

In a fresh Claude Code session, say:

> "I'm continuing the time-travel v1.0 build. Read the handoff at `/Users/macbook/Documents/Chris developed Applications /time-travel/handoffs/2026-05-28-plan-a-complete.md` and write Plan B."
