# Handoff: Plan B Complete — Audit Summary (for Fable 5 review)

**Date:** 2026-07-05
**Repo:** `github.com/Chrisamansood/time-travel`
**Purpose:** Summarize everything built this session for an external quality/architecture audit. Every judgment call made without explicit spec backing is called out below — treat those as the highest-value places to scrutinize.

---

## 1. What was accomplished

Plan B (engine + renderers) is now complete end-to-end, B1 through B7. Plan A (foundation) and B1–B5 (renderers, personas, search, providers) existed before this session; **B6 (synthesis) and B7 (orchestrator + CLI wiring) were built in this session**, plus one bug found and fixed via manual smoke testing.

| Phase | What it does | Built when |
|---|---|---|
| A | `Report` dataclass, CLI arg parser, provider ABC | Pre-existing |
| B1–B2 | HTML/Markdown/exec-pager renderers + Jinja2 templates | Pre-existing |
| B3 | Persona library (22 personas) + roster selection | Pre-existing |
| B4 | Tavily web search adapter | Pre-existing |
| B5 | Anthropic/OpenAI/Gemini/stub LLM provider adapters | Pre-existing (committed this session — was sitting uncommitted) |
| **B6** | **`synthesis.py`** — dedupe risk claims, classify Confirmed/Inflated/Buried, confidence math | **This session** |
| **B7** | **`orchestrator.py`** — six-phase pipeline; **`cli.py`** wiring for `run`/`render` | **This session** |

**End state, verified by running the actual CLI (not just pytest):**

```bash
time-travel run "<plan text or file>" --provider stub --search stub --output ./out
```

produces `report.json`, `report.html`, `report.md` (+ `exec.md` on `--for-exec`) in `./out/<timestamp>/`, fully offline, in ~0.7 seconds. `time-travel render <report.json>` re-renders without any provider.

**Test suite:** 137 tests passing, up from 102 at session start:
- +17 for `synthesis.py` (B6)
- +12 for `orchestrator.py` + CLI wiring (B7): 9 orchestrator end-to-end/unit tests, 3 CLI wiring tests
- +6 for the stub-search bug fix (§1, found via manual smoke test): 3 unit tests for `StubSearch`, 3 for the provider/search resolver functions

`mypy` and `ruff` clean on every file touched this session (see §4 for pre-existing gaps elsewhere).

### Commits this session (all on `origin/main`, pushed)

```
553d9dc  feat: implement Plan B B1-B5 — renderers, personas, search, providers  (committed uncommitted work)
b0204bc  feat: implement Plan B6 — synthesis (dedupe, classify, confidence math)
8e074bd  feat: implement Plan B7 — orchestrator, CLI wiring, offline stub search
a26ec51  chore: bump Claude Code plugin version to 0.1.1  (NOT YET PUSHED — see §5)
```

---

## 2. Architecture as built

```
run(source, opts, provider?, search?) -> Report
  Phase 0   _ingest_plan          — file path, inline text, or stdin -> (title, text)
  Phase 1   _phase1_user_pov_and_blind_spots  — 1 LLM call -> UserPOV + blind-spot candidates
  Phase 2   select_roster + _phase2_evidence  — pick 5-7 personas, 1 search call each
  Phase 3   _phase3_persona_fanout     — N parallel LLM calls -> PersonaRiskClaim list
  Phase 3.5 _phase3_5_rebuttal         — 1 LLM call -> Rebuttal
  Phase 4   classify_risks + compute_confidence + _phase4_revised_plan
  Phase 5   render_html/markdown/exec_to_file, write report.json + process.log
```

`synthesis.py` is pure functions (no I/O), independently tested: `classify_risks(claims, blind_spot_candidates) -> (confirmed, inflated, buried)` and `compute_confidence(confirmed_risks, mitigated_risk_ids) -> (unmitigated, mitigated)`.

Provider/search resolution order: explicit kwarg (dependency injection, used by all tests) → `--provider`/`--search` flag → `TIME_TRAVEL_PROVIDER` env var → first provider with an API key set → Anthropic default. `--provider stub` / `--search stub` fully bypass the network.

---

## 3. Judgment calls made without explicit spec backing

The Plan B spec (`docs/superpowers/specs/2026-06-06-plan-b-engine-and-matrix-renderer.md`) locked the renderer, persona, search, and provider designs in detail, but **left the synthesis input contract and the orchestrator's LLM-call shapes undefined** (B6/B7 didn't exist yet when the spec was written, and nothing upstream produced "raw persona output" for synthesis to consume). These are the decisions an auditor should pressure-test hardest:

1. **`PersonaRiskClaim` shape** (`synthesis.py`) — I invented this as the minimal structure a persona's risk mention needs (name, severity, likelihood, citations, tripwire, change-my-mind, mitigation, owner). Nothing forced this exact shape; a richer or different shape is equally defensible.
2. **Classification rule** — Confirmed requires **≥2 personas agreeing by exact/case-insensitive name match AND at least one citation**; anything else (single persona, or multiple personas with zero citations) becomes Inflated. This is a literal reading of the spec's one sentence on this ("Confirmed: ≥2 personas agree, evidence exists") but the spec gives no guidance on near-duplicate name matching (e.g. "Budget overrun" vs "Cost overrun" would NOT merge — only exact/case-insensitive matches do).
3. **Confidence math formula** — the spec says confidence should be "computed from risk count, severity distribution, and mitigation coverage" but gives no formula. I implemented: each confirmed risk applies a severity-weighted penalty (severity_fraction × 100/6, so ~6 max-severity risks floors confidence at 0); mitigating a risk recovers half its penalty. This is untested against any real-world calibration — it's internally consistent (monotonic, bounded 0–100) but the actual numbers it produces have not been validated against what a human would rate.
4. **Buried-risk sourcing** — I fold blind-spot detection into Phase 1's single LLM call (asking for both `user_pov` and `blind_spots` in one JSON response) rather than a dedicated Phase. This keeps Phase 1 to "a single LLM call" as the spec literally says, but conflates two different information asks into one prompt, which may hurt LLM output quality in practice.
5. **Evidence extraction is shallow** — `EvidenceItem` (title/url/when/who/what_happened/why_relevant) is populated directly from raw search-result snippets with no LLM interpretation pass. `when`/`who` are always empty strings. The spec's `EvidenceItem` model implies richer analogue-case extraction than a raw search snippet provides.
6. **`_ingest_plan` auto-detect** — spec help text says the plan source arg is "Omit for auto-detect" without defining what that means. I implemented: file path if it exists on disk, else stdin if piped, else treat the string as inline plan text. Untested against real interactive use.
7. **Revised-plan generation** — one extra LLM call (not explicitly named as a phase in the spec's six-phase list) asking the provider to rewrite the plan given the mitigation list. If no confirmed risks exist, it's skipped and the original plan text is returned unchanged.

None of these are exercised by real LLM calls in tests (all tests use `StubProvider`/`StubSearch`/`FakeSearch`), so **the actual prompt quality and JSON-parsing robustness against real Anthropic/OpenAI/Gemini responses is unverified.** The stub provider returns either a fixed canned string or a plain-text fallback — it never returns malformed JSON, truncated JSON, or JSON wrapped in explanatory prose the way a real model sometimes does. `_try_json` has a bare `except (json.JSONDecodeError, ValueError): return None` fallback everywhere, so bad output degrades to empty results rather than crashing — but this has not been tested against real model output.

---

## 4. Known gaps / pre-existing debt (not touched this session, flagged not fixed)

- `mypy src/` reports 7 errors, all pre-existing in B5 provider adapters (`anthropic_provider.py`, `openai_provider.py`, `gemini_provider.py`) — type mismatches in the actual API call sites, not exercised by contract tests since those mock the client.
- `ruff check` reports 23 pre-existing line-length/import-order issues, concentrated in `personas/library.py` (long persona description strings) and `personas/selection.py` (unused import, import order).
- These predate this session's work (verified: same errors present before B6/B7 were touched) and were left alone per "don't fix what you weren't asked to touch."

---

## 5. Repo state

- `origin/main` is in sync with local `main` through `8e074bd` (all of Plan B).
- **One commit is local-only, not yet pushed:** `a26ec51` (Claude Code plugin version bump 0.1.0 → 0.1.1, needed to force `claude plugin update` to actually pull the stale cached skill content). Low-risk, trivial diff — push whenever convenient.
- The Claude Code **skill** (`harnesses/claude-code/plugins/time-travel/`) is a separate, markdown-only implementation of the premortem process that Claude follows directly — **it does not call the Python engine built this session.** They are two independent implementations of the same idea (CLI engine vs. in-context skill). No decision has been made on whether/how to unify them.

---

## 6. What's next

1. **Plan C** (per spec, not started): harness wrappers for other CLI targets (Codex skill stub exists but is unwired), install script, GitHub Actions CI, README, `scripts/smoke-test.sh` for manual live-API testing.
2. **Real-provider validation** — run `time-travel run` against actual Anthropic/OpenAI/Gemini APIs at least once to test whether §3's prompt/parsing assumptions survive contact with real model output (malformed JSON, prose-wrapped JSON, etc.). This is the biggest unverified risk in the current build.
3. **Decide on skill/engine unification** — should the Claude Code skill eventually shell out to this Python engine, stay independent, or should the engine become the reference implementation the skill's prompts are checked against?
4. **Push `a26ec51`** to `origin/main`.
5. Optional: calibrate the confidence-math formula (§3.3) against a few real premortems to see if the numbers feel right, or replace it with something spec-driven if Chris has a preferred model.

---

## Related

- [[2026-05-28-plan-a-complete]] — Plan A handoff
- [[2026-06-06-plan-b-spec-complete]] — Plan B spec + build sequence
- `docs/superpowers/specs/2026-06-06-plan-b-engine-and-matrix-renderer.md` — the spec this session implemented against
