# Time-Travel v1.0 — Cross-Harness Premortem with HTML Reports

**Status:** Draft for review
**Author:** Chris Sood
**Date:** 2026-05-26
**Repo:** github.com/chrisaman/time-travel (existing, MIT-licensed, currently v0.1.0)

## 1. Goals

Evolve the existing `time-travel` Claude Code plugin into a **provider-agnostic Python tool** that:

1. Produces a **premium, single-file HTML report** alongside the existing Markdown report.
2. Runs from **multiple harnesses** (Claude Code, Codex CLI, raw Python CLI) and **multiple LLM providers** (Anthropic, OpenAI, Gemini) via a shared Python engine.
3. Is **GitHub-ready**: `pip install time-travel-premortem` + one-line skill installer, MIT license, CI on three Python versions, runnable in under five minutes from a clean checkout.

The current v0.1.0 is Claude-Code-only and writes Markdown only. v1.0 keeps every behavior of the premortem flow but moves the orchestration into Python so it stops being harness-locked.

## 2. Non-goals (v1.0)

- Gemini CLI wrapper (the harness, distinct from the Gemini provider adapter). Leave a stub directory but do not implement.
- Native PDF rendering. Use browser print-to-PDF from the HTML.
- Web UI or hosted service.
- Persona authoring tool. Personas remain as Python dataclasses in `personas/library.py`.
- Streaming/progress UI. CLI prints phase headers via `rich`; no live token streaming.
- Wholesale rewrite of the premortem methodology. The six-phase flow, persona library, severity lenses, classification scheme, and confidence math stay as-is — they are the proven IP of v0.1.0.

## 3. Locked-in decisions (from brainstorming)

| Topic | Decision |
|---|---|
| Harness scope | Provider-agnostic. Anthropic + OpenAI + Gemini APIs. |
| Report formats | HTML + Markdown, both always rendered. |
| Implementation language | Python (≥3.10). |
| HTML aesthetic | Neutral editorial (Vercel/Stripe/Linear feel — not Chris-personal brand). |
| Provenance | Evolve own MIT-licensed work. No attribution complexity. |
| Work location | `/Users/macbook/Documents/Chris developed Applications /time-travel`, evolved in place. Push to existing `github.com/chrisaman/time-travel`. |
| Engine model | Python runner is the single engine. Harness skill files are thin wrappers that shell out via Bash. |
| Repo shape | Polyglot monorepo (Approach A). One repo, `src/` for engine, `harnesses/` for wrappers. |
| Web search | Tavily only in v1.0. The `search/` abstraction is structured to add Brave/Serper later without engine changes. |
| HTML packaging | Single self-contained `.html` file with inlined CSS/JS. ~80–150 KB. |
| HTML interactivity | Minimal vanilla JS: tabs, collapsibles, severity-dot tooltips (~3 KB inlined). |

## 4. Architecture

### 4.1 Layered view

```
Front-ends (where users enter)
  ├─ Claude Code skill (thin wrapper)
  ├─ Codex CLI skill (thin wrapper)
  └─ Direct CLI / Python import
        │
        ▼
  time_travel.cli  (argparse, config, dispatch)
        │
        ▼
  orchestrator.run(plan, opts)
    Phase 0  Ingest plan
    Phase 1  User-POV pass
    Phase 2  Persona roster + evidence pack
    Phase 3  Persona fan-out (asyncio.gather)
    Phase 3.5 Rebuttal round
    Phase 4  Synthesis → canonical Report
    Phase 5  Render artifacts
        │
        ▼
  ┌───────────┬───────────┬──────────────┐
  │ providers │  search   │   render     │
  │ (LLM)     │  (web)    │  (html/md)   │
  ├───────────┼───────────┼──────────────┤
  │ anthropic │ tavily    │ jinja2 →     │
  │ openai    │           │   report.html│
  │ gemini    │           │   report.md  │
  └───────────┴───────────┴──────────────┘

v1.0 ships Tavily only. The `search/base.py` abstraction is
designed so Brave/Serper can be added as adapters in v1.1 without
engine changes.
```

### 4.2 Canonical data model

Phase 4 produces one `Report` dataclass. Both renderers consume it. JSON-serializable so `time-travel render <report.json>` is a valid recovery/re-render command.

```python
@dataclass
class Report:
    plan_title: str
    plan_source: str
    generated_at: datetime
    horizons: list[str]
    plan_text: str

    user_pov: UserPOV
    personas: list[PersonaActivation]
    narratives: dict[str, dict[str, str]]   # persona -> horizon -> text

    confirmed_risks: list[Risk]
    inflated_risks: list[InflatedRisk]
    buried_risks: list[BuriedRisk]

    rebuttal: Rebuttal
    mitigations: list[Mitigation]
    revised_plan: str
    evidence: list[EvidenceItem]

    unmitigated_confidence: int          # 0-100
    mitigated_confidence: int            # 0-100
    flags_used: dict
    process_log_path: str | None
    exec_pager_path: str | None
```

`Risk`, `UserPOV`, `Rebuttal`, etc. are sub-dataclasses with the same fields the existing report template demands (severity vector T/U/B/O/F/S, likelihood, urgency, tripwire, "what would change my mind", mitigation, owner shape, citations).

### 4.3 Module map

| Module | Responsibility | LoC target |
|---|---|---|
| `src/time_travel/cli.py` | argparse, config loading, dispatch | ~150 |
| `src/time_travel/orchestrator.py` | Six-phase pipeline | ~300 |
| `src/time_travel/models.py` | `Report` and sub-dataclasses | ~150 |
| `src/time_travel/providers/base.py` | `LLMProvider` ABC | ~50 |
| `src/time_travel/providers/anthropic_provider.py` | Anthropic adapter, includes prompt caching | ~120 |
| `src/time_travel/providers/openai_provider.py` | OpenAI adapter | ~120 |
| `src/time_travel/providers/gemini_provider.py` | Gemini adapter | ~120 |
| `src/time_travel/search/base.py` + `tavily.py` | Web search abstraction + Tavily impl | ~100 |
| `src/time_travel/personas/library.py` | Persona definitions as dataclasses | ~300 |
| `src/time_travel/personas/selection.py` | Roster picker (universal + domain) | ~80 |
| `src/time_travel/synthesis.py` | Dedupe, classify, confidence math | ~250 |
| `src/time_travel/render/html.py` | Jinja2 + inlining + minification | ~150 |
| `src/time_travel/render/markdown.py` | Jinja2 → Markdown | ~100 |
| `src/time_travel/render/exec_pager.py` | ≤300-word one-pager + word-count enforcement | ~80 |
| `src/time_travel/templates/report.html.j2` | HTML template | — |
| `src/time_travel/templates/report.md.j2` | Markdown template | — |
| `src/time_travel/templates/exec.md.j2` | Exec one-pager template | — |
| **Total Python** | | **~2,000 LoC + templates** |

### 4.4 Repo structure

```
time-travel/
├── README.md
├── LICENSE                     # MIT (existing)
├── CHANGELOG.md
├── pyproject.toml              # PEP 621, console script entry point
├── .gitignore
├── .pre-commit-config.yaml     # ruff + black + mypy
├── src/time_travel/            # engine (Section 4.3)
├── tests/                      # pytest, fixtures, golden files
├── examples/
│   ├── sample-plan.md          # input fixture
│   └── sample-report.html      # golden output (committed for preview)
├── docs/
│   ├── architecture.md         # what's here is the high-level; this spec is one input
│   └── superpowers/specs/      # this spec lives here
├── harnesses/
│   ├── claude-code/
│   │   └── plugins/time-travel/
│   │       ├── .claude-plugin/plugin.json
│   │       └── skills/time-travel/SKILL.md   # ~50 LoC thin wrapper
│   ├── codex/
│   │   └── skills/time-travel/SKILL.md
│   └── gemini/                 # stub directory only in v1.0
└── scripts/
    ├── install-skills.sh       # symlink wrappers into ~/.claude, ~/.codex
    └── smoke-test.sh           # one-shot end-to-end against real Anthropic API
```

## 5. The HTML report

### 5.1 Layout (top-to-bottom, single scrollable page)

1. **Header strip** — `Time Travel · {plan_title}`, generation timestamp, persona count, horizons, [download .md] / [print/PDF] buttons.
2. **Confidence band** — `Unmitigated X% → With mitigations Y%` with horizontal bar visualization. Color transitions red → amber → green.
3. **TL;DR** — top 3 failures (numbered, one-line each) + the Buried risk.
4. **User-POV pass** — 2×2 grid of cards: What they thought / Would forgive / Untrustworthy / Predictable complaints.
5. **Personas activated** — chip row with name + 1-line rationale tooltip.
6. **Timeline narratives** — collapsible per-persona section, default closed. Click persona → expand 3 horizon cards.
7. **Risk classification** — tabs: `[Confirmed] [Inflated] [Buried]`. Confirmed shows a table with severity dots (●●●○○○ T/U/B/O/F/S, hover for breakdown), likelihood, urgency, mitigation, owner shape.
8. **Mitigations — this week** — numbered, action-oriented list.
9. **Revised plan** — original plan with injected mitigations marked by a left border + subtle tint.
10. **Evidence pack** — analogue cases (with external-link icon) + cited persona quotes.
11. **Methodology** — flags used, paths to MD report + process log.

### 5.2 Visual language

- Typography: system font stack only (no web-font fetching, since the HTML is fully self-contained). Body: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`. Data/code: `ui-monospace, SFMono-Regular, "Menlo", monospace`.
- Palette (5 colors): `#0f172a` ink, `#475569` secondary text, `#fafafa` canvas, `#e5e7eb` borders, `#0ea5e9` accent.
- Severity dots: green (0–1) → amber (2) → red (3).
- 720 px content column, generous whitespace, one-page scroll.
- Light + dark mode via `prefers-color-scheme`.
- Print: `@media print` strips chrome, expands all collapsibles. HTML doubles as print-to-PDF source.

### 5.3 Packaging

- Single self-contained `.html` file. CSS and JS inlined at render time by `render/html.py`. No external assets, no CDN dependencies. Target ~80–150 KB.
- JS budget: ~3 KB inlined (tabs, collapsibles, tooltips). Vanilla, no frameworks.

## 6. Provider adapters

`LLMProvider` ABC defines two methods:

```python
class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        **kwargs,
    ) -> str: ...

    @abstractmethod
    async def complete_parallel(
        self,
        calls: list[dict],   # [{"prompt": ..., "system": ..., "model": ...}, ...]
    ) -> list[str]: ...
```

`complete_parallel` lets each adapter optimize: Anthropic uses message batching with caching, OpenAI uses async client + `asyncio.gather`, Gemini uses its async client. From the orchestrator's view, both phases 3 and 3.5 are just `await provider.complete_parallel(persona_calls)`.

**Provider selection:** `--provider` flag, falls back to `TIME_TRAVEL_PROVIDER` env var, falls back to the first provider with an API key set in env. Resolution order when multiple keys are set: **Anthropic → OpenAI → Gemini**. Default model per provider is hardcoded but overridable via `--model`.

**API keys:** Env vars only — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`. No config files in v1.0.

## 7. Harness wrappers

### 7.1 Claude Code

`harnesses/claude-code/plugins/time-travel/skills/time-travel/SKILL.md` keeps the existing frontmatter (so triggers and description are unchanged for users) but the body shrinks from ~200 LoC to ~50:

1. Resolve plan source (auto-detect order from v0.1.0 preserved).
2. Run `time-travel run <plan> --output ./time-travel-reports` via Bash.
3. Parse stdout for the TL;DR JSON block.
4. Print TL;DR + paths in chat.

All Phase 0–5 logic moves to the Python engine. The `Agent` parallel-dispatch tool is no longer used — the engine handles parallelism internally via asyncio.

### 7.2 Codex CLI

`harnesses/codex/skills/time-travel/SKILL.md` mirrors the Claude Code version, swapping any harness-specific tool names per the `codex-tools.md` mapping convention.

### 7.3 Install script

```bash
#!/usr/bin/env bash
# scripts/install-skills.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"

# Claude Code
mkdir -p ~/.claude/plugins
ln -sfn "$REPO/harnesses/claude-code/plugins/time-travel" ~/.claude/plugins/time-travel

# Codex
mkdir -p ~/.codex/skills
ln -sfn "$REPO/harnesses/codex/skills/time-travel" ~/.codex/skills/time-travel

echo "Skill wrappers symlinked."
echo "Next: pip install -e . to install the engine."
```

Symlinks (not copies) so edits in the repo are live in the harness without reinstalling.

## 8. CLI surface

```
time-travel run [SOURCE] [--provider P] [--model M] [--search S]
                [--fast] [--horizons H1,H2,H3] [--output PATH]
                [--for-exec] [--ai-source] [--no-process-log]
                [--format html,md,json]

time-travel render REPORT.json [--format html,md] [--output PATH]
                # Re-render from a saved JSON; no LLM calls.

time-travel personas list             # Inspect built-in roster
time-travel doctor                    # Verify env vars, deps, network
```

`time-travel run` is the v0.1.0 contract preserved. New flags: `--provider`, `--search`, `--format`. New subcommands: `render`, `personas`, `doctor`.

## 9. Packaging and distribution

- **PyPI name:** `time-travel-premortem` (since plain `time-travel` is likely taken). Console script stays just `time-travel`.
- **Install:** `pip install time-travel-premortem` for the engine. `git clone … && ./scripts/install-skills.sh` for harness wrappers.
- **Dependencies (pinned major versions):** `anthropic>=0.30`, `openai>=1.50`, `google-genai>=0.5`, `tavily-python>=0.5`, `jinja2>=3.1`, `rich>=13`, `dataclasses-json>=0.6`, `pydantic>=2` (for env config). Optional dev: `pytest`, `pytest-asyncio`, `ruff`, `black`, `mypy`, `pre-commit`.
- **Python versions:** 3.10, 3.11, 3.12 (CI matrix).

## 10. Testing strategy

| Layer | Tests | Run in CI? |
|---|---|---|
| `synthesis.py` | Unit tests for dedupe, classification, confidence math. Pure logic, no LLM. | Yes |
| `render/html.py` and `render/markdown.py` | Snapshot tests: feed fixed `Report` JSON, diff against golden file. | Yes |
| `providers/*.py` | Contract tests via a fake `LLMProvider` adapter. Each provider's adapter is tested for its parsing of provider-specific response shapes using recorded fixtures. | Yes |
| End-to-end | One full-pipeline test using a stub provider that returns canned persona responses. Exercises orchestrator wiring without spending API tokens. | Yes |
| Live API | `scripts/smoke-test.sh` runs against real Anthropic API. Manual only. | No |

No live API tests in CI (cost + flakiness). The end-to-end stub test catches integration regressions.

## 11. CI / GitHub Actions

- `test.yml` — pytest on Python 3.10/3.11/3.12, lint with ruff, type-check with mypy. Required for merge.
- `release.yml` — on tag `v*`, build sdist + wheel, publish to PyPI via trusted publishing (no API token in secrets).
- `render-example.yml` — on PR, run engine against `examples/sample-plan.md` with stub provider, upload the HTML artifact for visual review.

## 12. README structure

What a GitHub visitor sees:

1. One-line value prop.
2. Animated GIF or screenshot of the HTML report.
3. `pip install time-travel-premortem`
4. `time-travel run my-plan.md`
5. Sample TL;DR output.
6. One-paragraph "how it works" (six phases summary, link to architecture.md).
7. "Inside Claude Code / Codex" section with the install-skills.sh one-liner.
8. Provider configuration (env vars).
9. License + acknowledgments.

Target: a new visitor goes from landing on the README to a rendered HTML report in **under five minutes**.

## 13. v1.0 release criteria

The release is ready when:

1. `pip install time-travel-premortem && time-travel run examples/sample-plan.md` works end-to-end with at least the Anthropic provider.
2. HTML report renders correctly in Chrome, Safari, Firefox, and prints to PDF cleanly.
3. Markdown report matches v0.1.0's information density (no regressions in the existing template's content).
4. All three providers (Anthropic, OpenAI, Gemini) pass the contract tests.
5. Claude Code and Codex skill wrappers install via `scripts/install-skills.sh` and trigger correctly on the documented phrases.
6. CI is green on Python 3.10, 3.11, 3.12.
7. README walks a new user from zero to first report in under five minutes (measured with a fresh clone + fresh venv).

## 14. Migration from v0.1.0

The existing local folder at `/Users/macbook/Documents/Chris developed Applications /time-travel` is not currently a git repo. Migration steps (deferred to the implementation plan):

1. `git init` in the existing folder.
2. Add `pyproject.toml`, `src/`, `tests/`, etc.
3. Move existing `plugins/time-travel/` content under `harnesses/claude-code/plugins/time-travel/`, rewriting `SKILL.md` to be the thin wrapper described in §7.1.
4. Convert `references/persona-library.md`, `references/severity-lenses.md`, etc. into Python in `src/time_travel/personas/library.py` and friends. Keep a `docs/` copy of the markdown for human reading.
5. Connect to `github.com/chrisaman/time-travel` remote. If remote has v0.1.0 content, reconcile via a `main` reset or by branching from upstream.
6. First push: tag `v1.0.0-rc.1`, push, validate CI.
7. Delete the duplicate folder at `/Users/macbook/Documents/Developed Skills /time-travel`.
8. Regenerate the Codex skill at `/Users/macbook/.codex/skills/time-travel` via the install script (it becomes a symlink).

## 15. Risks and open questions

- **Upstream GitHub repo state unknown.** The plugin.json claims homepage `github.com/chrisaman/time-travel`, but I have not verified what is actually in the remote. Resolution: implementation plan must include a "check remote first" step before reconciling.
- **Tavily free tier limits.** Tavily's free tier is generous but bounded. If a typical run hits 3–5 searches, that's ~30–50 searches per 10 reports per month at free tier limits. May need to surface a "Tavily quota exceeded" error gracefully.
- **Token costs across providers.** A full premortem run with 6 personas × ~2,000 tokens × 2 rounds = ~25 K input + ~15 K output per provider call. Per-run cost is bounded but non-trivial. README must show estimated cost per run.
- **Persona library as code vs markdown.** Moving personas from MD to Python loses some readability for contributors who want to add a persona without touching code. Mitigation: ship a one-page `docs/contributing-personas.md` with the dataclass schema explained.
- **HTML report bloat with large plans.** A very long plan could produce a 500 KB+ HTML file. Hard cap and warning at 250 KB; consider compression or summarization if exceeded.

## 16. Out-of-scope follow-ups (v1.1+)

- Gemini CLI native skill wrapper (harness #3).
- Native PDF export (currently via browser print).
- Persona library marketplace / community contributions.
- Streaming progress in the CLI (per-phase token counts).
- VS Code extension that runs the skill inline.
- Hosted web service.
