# Handoff: time-travel v1.0 — Plan B Spec Complete

**Date:** 2026-06-06
**Session outcome:** Plan B fully designed and spec written. Ready for implementation.

---

## What was accomplished

- Reviewed Plan A handoff and confirmed 40 tests passing, repo live
- Decided to absorb HTML renderer into Plan B (was originally Plan C)
- Locked all design decisions for the matrix HTML dashboard
- Wrote and committed Plan B spec to `docs/superpowers/specs/2026-06-06-plan-b-engine-and-matrix-renderer.md`

---

## Key decisions locked

| Decision | Choice |
|---|---|
| Output contract | `report.html` + `report.md` + `report.json` always emitted; `exec.md` on `--for-exec` |
| HTML aesthetic | Gunmetal Terminal — `#111418` bg, `#F0F6FC` body, `#00D26A` accent only |
| Effects | Static + tasteful — monospace headlines, `> ` eyebrows, `//` labels, `────` ASCII dividers, severity dots `●●●○○○`. No animations, no canvas, no glow |
| Layout | Multi-pane terminal dashboard, ≥1200px screen-only. Below ~900px: "best viewed wide" notice |
| Print | Screen-only HTML — `.md` is the printable artifact |
| Footer | Hardcoded watermark on every HTML report: `Chris Sood · Agentic AI Strategy` + X / Medium / LinkedIn links |
| Build sequence | **Renderer-first** — HTML dashboard built against hand-crafted fixture before any engine code |
| Plan C scope | Harnesses, install script, CI workflows, README, smoke tests (renderers no longer deferred) |

---

## All files created/modified

```
time-travel/
├── docs/superpowers/specs/2026-06-06-plan-b-engine-and-matrix-renderer.md  ← Plan B spec (NEW)
└── handoffs/2026-06-06-plan-b-spec-complete.md                             ← this file (NEW)
```

### Git log (this session)
```
0ea8d2c  docs: add Plan B spec — engine + matrix HTML renderer
```

---

## Plan B build sequence

| Phase | Deliverable | Notes |
|---|---|---|
| B1 | `examples/sample-report.json` fixture + `render/html_matrix.py` + `templates/report.html.j2` + snapshot test | Start here. No LLM needed. |
| B2 | `render/markdown.py`, `render/exec_pager.py`, templates, snapshot tests | exec.md ≤300 words enforced |
| B3 | `personas/library.py`, `personas/selection.py`, unit tests | Convert `references/persona-library.md` to dataclasses |
| B4 | `search/base.py`, `search/tavily.py`, contract tests | Mock Tavily client in tests |
| B5 | `providers/anthropic_provider.py` (prompt caching), `openai_provider.py`, `gemini_provider.py`, `providers/stub_provider.py`, contract tests | No live API in CI |
| B6 | `synthesis.py`, unit tests | Pure functions, no I/O |
| B7 | `orchestrator.py`, wire `cli.py` `run` command, end-to-end test with stub provider | End state: full pipeline works |

---

## Gotchas

1. **Working directory has a trailing space:** Always quote — `"/Users/macbook/Documents/Chris developed Applications /time-travel"`
2. **Venv:** `.venv/` in repo root — `source .venv/bin/activate` before running Python
3. **GitHub remote is live:** `git push origin main` works (gh auth done in user's terminal)
4. **Persona library source:** `harnesses/claude-code/plugins/time-travel/skills/time-travel/references/persona-library.md` — convert to Python in B3, don't rewrite
5. **Report dataclass constraints from Plan A:**
   - `Risk.mitigation_summary` (NOT `Risk.mitigation`)
   - `flags_used: dict[str, bool]` on Report
   - `generated_at` — naive datetimes only (no timezone-aware on Python <3.11)
6. **Footer social links (hardcoded in template):**
   - X: `https://x.com/Sood_Chris`
   - Medium: `https://chrisamansood.medium.com/`
   - LinkedIn: `https://www.linkedin.com/in/chrisamansood/`
7. **Target test count:** ~60 new tests in Plan B → ~100 total
8. **Snapshot test golden update:** `pytest --update-golden` regenerates golden files when template changes are intentional

---

## How to restart

Paste this prompt into a new Claude Code session:

> "I'm implementing Plan B of the time-travel v1.0 build. Read the handoff at `/Users/macbook/Documents/Chris developed Applications /time-travel/handoffs/2026-06-06-plan-b-spec-complete.md` and the spec at `/Users/macbook/Documents/Chris developed Applications /time-travel/docs/superpowers/specs/2026-06-06-plan-b-engine-and-matrix-renderer.md`, then write the Plan B implementation plan and execute it phase by phase starting with B1."
