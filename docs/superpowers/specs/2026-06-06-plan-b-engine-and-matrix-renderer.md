# Time-Travel v1.0 — Plan B: Engine + Matrix HTML Renderer

**Status:** Approved for implementation
**Author:** Chris Sood
**Date:** 2026-06-06
**Repo:** github.com/Chrisamansood/time-travel
**Predecessor:** `2026-05-26-time-travel-cross-harness-design.md` (original v1.0 spec)
**Handoff:** `handoffs/2026-05-28-plan-a-complete.md`

---

## 1. Goal

After Plan B, `time-travel run examples/sample-plan.md --provider anthropic` produces three files in `./time-travel-reports/<timestamp>/`:

1. `report.html` — a self-contained matrix-style terminal dashboard (screen-only, ≥1200px)
2. `report.md` — the full premortem report as Markdown (printable artifact)
3. `exec.md` — a ≤300-word executive one-pager (only when `--for-exec` flag is set)

`time-travel render examples/sample-report.json` also works — re-renders from a saved JSON without LLM calls.

---

## 2. Scope changes from original spec

The original spec deferred HTML/MD rendering to Plan C. Plan B now absorbs the renderers. The revised plan sequence is:

| Plan | Scope |
|---|---|
| **A** | Foundation — monorepo, `Report` dataclass, CLI scaffolding, 40 tests ✅ |
| **B** | Engine + both renderers (this spec) |
| **C** | Harness wrappers, install script, CI workflows, README, smoke tests |

---

## 3. Output contract

Both renderers consume one `Report` dataclass (locked in Plan A, `src/time_travel/models.py`). The JSON round-trip (`Report.to_json()` / `Report.from_json()`) is the interface between engine and renderers.

```
Report (JSON on disk)
  ├── render/html_matrix.py  →  report.html
  ├── render/markdown.py     →  report.md
  └── render/exec_pager.py   →  exec.md  (--for-exec only)
```

---

## 4. Build sequence (renderer-first)

Renderer-first was chosen so the HTML dashboard can be iterated on cheaply (no LLM cost) before the engine is built. The `Report` dataclass is already locked, so the hand-crafted fixture won't drift.

| Phase | Deliverable | LLM calls? |
|---|---|---|
| **B1** | `examples/sample-report.json` fixture + `render/html_matrix.py` + `templates/report.html.j2` + snapshot test | No |
| **B2** | `render/markdown.py`, `render/exec_pager.py`, `templates/report.md.j2`, `templates/exec.md.j2`, snapshot tests | No |
| **B3** | `personas/library.py`, `personas/selection.py`, unit tests | No |
| **B4** | `search/base.py`, `search/tavily.py`, contract tests (mocked client) | No |
| **B5** | `providers/anthropic_provider.py`, `providers/openai_provider.py`, `providers/gemini_provider.py`, `providers/stub_provider.py`, contract tests | No (recorded fixtures) |
| **B6** | `synthesis.py`, unit tests | No |
| **B7** | `orchestrator.py`, wire `cli.py` `run` command, end-to-end test (stub provider) | No in CI |

Each phase is 1–2 commits. Target: ~14 commits total.

---

## 5. Module map

| Module | Responsibility | LoC target |
|---|---|---|
| `render/html_matrix.py` | Load Report → render Jinja2 template → write self-contained `.html` | ~120 |
| `render/markdown.py` | Load Report → render Jinja2 template → write `.md` | ~80 |
| `render/exec_pager.py` | Load Report → render exec template → enforce ≤300 words → write `exec.md` | ~60 |
| `templates/report.html.j2` | Master HTML template (includes CSS/JS partials) | — |
| `templates/report.md.j2` | Markdown report template | — |
| `templates/exec.md.j2` | Exec one-pager template | — |
| `personas/library.py` | Persona dataclasses converted from `references/persona-library.md` | ~250 |
| `personas/selection.py` | Roster picker: 2–3 universal + 3–4 domain-specific | ~70 |
| `search/base.py` | `WebSearch` ABC | ~30 |
| `search/tavily.py` | Tavily adapter | ~60 |
| `providers/anthropic_provider.py` | Async Anthropic calls with prompt caching | ~120 |
| `providers/openai_provider.py` | Async OpenAI calls | ~100 |
| `providers/gemini_provider.py` | Async Gemini calls | ~100 |
| `providers/stub_provider.py` | Returns canned persona strings for CI tests | ~40 |
| `synthesis.py` | Dedupe, classify (Confirmed/Inflated/Buried), confidence math | ~200 |
| `orchestrator.py` | Six-phase pipeline wiring all modules | ~280 |
| `cli.py` (update) | Wire `run` to `orchestrator.run()`, remove `NotImplementedError` | ~20 |
| **Total new Python** | | **~1,530 LoC** |

---

## 6. HTML matrix dashboard

### 6.1 Visual language

| Element | Value |
|---|---|
| Background | `#111418` charcoal |
| Body text | `#F0F6FC` near-white |
| Accent | `#00D26A` green — bars, dots, numbers, dividers ONLY |
| Secondary text | `#9198a1` |
| Muted / labels | `#444c56` |
| Card backgrounds | `#0d1117` |
| Borders | `#1e2329` |
| Font — headlines, labels, numbers | `ui-monospace, 'Courier New', monospace` |
| Font — body descriptions | `system-ui, -apple-system, sans-serif` |
| Eyebrow prefix | `> ` in green |
| Section labels | `//` prefix, 8px tracked uppercase |
| Dividers | `────────` ASCII, `#2a3038` |
| Severity dots | `●` filled / `○` empty — red=high(3), amber=mid(2), green=low(1) |
| Tab active state | Green text + 2px `#00D26A` bottom border |
| Risk cards | `#0d1117` bg, `1px solid #1e2329` border, no border-radius |

### 6.2 Layout (7 zones, top to bottom)

```
┌─ tt-top (3px #00D26A bar) ──────────────────────────────────────────┐
├─ tt-header ─────────────────────────────────────────────────────────┤
│  > TIME-TRAVEL · {plan_title}         {timestamp} · {n} PERSONAS    │
│  [↓ report.md]  [↓ exec.md]                        T+{horizons}    │
├─ tt-confidence ─────────────────────────────────────────────────────┤
│  UNMITIGATED {x}%  ══════════════╪══════════════  MITIGATED {y}%    │
│  ▲ {delta}pp lift · {n} mitigations applied                         │
├─ tt-rail (~200px) ──────┬─ tt-center ──────────────────────────────┤
│  // PERSONAS             │  [CONFIRMED n] [INFLATED n] [BURIED n]   │
│  {chip per persona}      │                                          │
│                          │  risk cards (JS tab-switched)            │
│  // HORIZONS             │  each card:                              │
│  ● T+3M (red dot)        │    num · title · description             │
│  ● T+6M (amber dot)      │    severity dots T/U/B/F (0–3 each)      │
│  ● T+12M (green dot)     │    owner · mitigation one-liner          │
├─────────────────────────┴──────────────────────────────────────────┤
│  // USER POV (2×2 grid)                                             │
│  [What they thought]  [Would forgive]                               │
│  [Untrustworthy]      [Predictable complaints]                      │
├─────────────────────────────────────────────────────────────────────┤
│  // MITIGATIONS THIS WEEK                                           │
│  01 {action}   02 {action}   03 {action}   04 {action}             │
├─────────────────────────────────────────────────────────────────────┤
│  // EVIDENCE & ANALOGUES             // METHODOLOGY                 │
│  {case · citation}                   flags · output paths           │
├─ tt-footer ─────────────────────────────────────────────────────────┤
│  Chris Sood · Agentic AI Strategy          X  Medium  LinkedIn      │
└─ tt-bot (2px #00D26A @ 35% opacity) ───────────────────────────────┘
```

### 6.3 Footer (watermark — hardcoded in template)

The footer is a mandatory, hardcoded watermark on every HTML report. It is not data-driven from the `Report` model. Social links are fixed:

- X: `https://x.com/Sood_Chris`
- Medium: `https://chrisamansood.medium.com/`
- LinkedIn: `https://www.linkedin.com/in/chrisamansood/`

Style: same dark treatment as header, monospace font, `1px solid #1e2329` top border, green accent on link hover.

### 6.4 Screen-only constraint

The HTML dashboard targets ≥1200px screens only. Below ~900px a notice renders: `// BEST VIEWED AT ≥1200px WIDTH`. No responsive CSS, no print stylesheet. The `.md` report is the printable artifact.

### 6.5 Packaging

Single self-contained `.html` file. All CSS and JS inlined at render time via Jinja2 `{% include %}`. No CDN dependencies, no external assets. Target: ~100–150 KB.

### 6.6 JS budget

~2 KB inlined vanilla JS — tab switching only. No frameworks, no animations, no canvas.

### 6.7 Jinja2 template structure

```
templates/
  report.html.j2          ← master template
  _css_matrix.css.j2      ← all styles ({% include %}-d and inlined)
  _js_tabs.js.j2          ← tab switching (~1 KB)
  _zone_header.html.j2
  _zone_confidence.html.j2
  _zone_risks.html.j2     ← loops confirmed/inflated/buried
  _zone_userpov.html.j2
  _zone_mitigations.html.j2
  _zone_evidence.html.j2
  _zone_footer.html.j2    ← hardcoded watermark
  report.md.j2
  exec.md.j2
```

### 6.8 Severity dot macro

```jinja2
{% macro severity_dots(label, score, colour) %}
<div class="tt-si">
  <span class="tt-sl">{{ label }}</span>
  {% for i in range(3) %}
    <span class="tt-d {{ colour if i < score else '' }}"></span>
  {% endfor %}
</div>
{% endmacro %}
```

`score` is 0–3. `colour` resolves: `r` (red) for score ≥2 on Timeline/Urgency/Financial lenses, `a` (amber) for score =1, `g` (green) for low-severity Buried risks.

---

## 7. Orchestrator — six-phase pipeline

```python
async def run(plan: str, opts: RunOptions) -> Report:
    # Phase 0: Ingest plan text, detect source type
    # Phase 1: User-POV pass — single LLM call
    # Phase 2: Persona roster selection + evidence query construction
    # Phase 3: Persona fan-out — asyncio.gather across all personas
    # Phase 3.5: Rebuttal round — each persona responds to others
    # Phase 4: Synthesis → canonical Report (dedupe, classify, confidence)
    # Phase 5: Render artifacts (html, md, exec if --for-exec)
    return report
```

`cli.py` calls `asyncio.run(orchestrator.run(plan, opts))` and prints the TL;DR block + output file paths to stdout.

---

## 8. Provider adapters

All three adapters implement the `LLMProvider` ABC from Plan A (`providers/base.py`):

```python
class LLMProvider(ABC):
    async def complete(self, prompt, system, model, max_tokens, **kwargs) -> str: ...
    async def complete_parallel(self, calls: list[dict]) -> list[str]: ...
```

| Adapter | Key implementation notes |
|---|---|
| `anthropic_provider.py` | Prompt caching on system prompt + persona library (cache_control="ephemeral"). Uses `asyncio.gather` for parallel persona calls. |
| `openai_provider.py` | Async OpenAI client + `asyncio.gather`. |
| `gemini_provider.py` | Async Gemini client. |
| `stub_provider.py` | Returns canned strings from a fixture dict keyed by persona name. Used in all CI tests — no API key required. |

Provider resolution order: `--provider` flag → `TIME_TRAVEL_PROVIDER` env var → first provider with API key set → Anthropic default.

---

## 9. Synthesis

`synthesis.py` is pure-function (no I/O, no LLM calls). It takes raw persona outputs and produces the classified risk lists and confidence scores that populate the `Report`.

Key operations:
- **Deduplicate** risks raised by multiple personas (same risk, different wording)
- **Classify** as Confirmed (≥2 personas agree, evidence exists), Inflated (raised but unsupported by evidence), or Buried (not raised by any persona — synthesiser injects based on plan blind spots)
- **Confidence math**: `unmitigated_confidence` and `mitigated_confidence` computed from risk count, severity distribution, and mitigation coverage

---

## 10. Testing strategy

| Phase | Test type | What is asserted |
|---|---|---|
| B1 | Snapshot | `render_html(fixture_report)` matches committed golden `examples/sample-report.html` |
| B2 | Snapshot | `render_markdown()` and `render_exec()` match golden files. Exec pager: unit test asserts ≤300 words enforced. |
| B3 | Unit | Persona selection: correct universal count (2–3), domain count (3–4), no duplicates, all required fields present |
| B4 | Contract | Tavily adapter: correct query construction, graceful error on quota exceeded, result shape matches `SearchResult` dataclass |
| B5 | Contract | Each adapter: correct API call shape, prompt caching headers sent (Anthropic), parallel calls use gather, errors propagate cleanly |
| B6 | Unit | Dedupe removes exact and near-duplicates, classification rules are deterministic, confidence stays 0–100 |
| B7 | End-to-end | Stub provider → full orchestrator → valid `Report` produced → both HTML and MD files written to output dir |

**Golden file update workflow:** `pytest --update-golden` regenerates committed golden files when a template change is intentional. Treated as a code change — reviewed in the PR diff.

**Not tested in CI:** live API calls. Covered by `scripts/smoke-test.sh`, run manually before any release tag.

**Target test count after Plan B:** ~100 total (40 from Plan A + ~60 new).

---

## 11. Key constraints carried from Plan A

- `Risk.mitigation_summary` (NOT `Risk.mitigation`) — renamed to avoid clash with `Mitigation` class
- `flags_used: dict[str, bool]` on `Report`
- `generated_at` uses naive datetimes only (timezone-aware not safe on Python <3.11)
- Working directory has a trailing space: always quote — `"/Users/macbook/Documents/Chris developed Applications /time-travel"`
- Venv at `.venv/` in repo root — `source .venv/bin/activate` before running Python

---

## 12. End state of Plan B

`time-travel run examples/sample-plan.md --provider anthropic` completes successfully and writes:

```
./time-travel-reports/2026-06-06T120000/
  report.html    ← matrix dashboard, opens in any browser at ≥1200px
  report.md      ← full markdown report
  report.json    ← canonical Report JSON (re-renderable with `time-travel render`)
```

All 100 tests pass. `ruff` and `mypy` clean.
