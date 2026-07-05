# Handoff: Time-Travel Unification Complete (T1-T6)

**Date:** 2026-07-05
**Repo:** `github.com/Chrisamansood/time-travel`
**Scope:** Unify the markdown skill and Python engine per
`docs/handoff/time-travel-audit.md` (findings C1-C6) — engine becomes the
single source of truth for classification/dedup/confidence/rendering; skill
becomes a thin harness that emits a claims JSON and shells out to the engine.

---

## What was done, per task

### T1 — Fuzzy classification semantics in the engine (fixes audit C1/C2)
`synthesis.py` no longer dedupes by exact/case-insensitive name. Family
merging is now fuzzy: token-sort-ratio (via stdlib `difflib`, no new
dependency) on `name` at threshold 0.6, with a mechanism check that keeps
same-named claims separate when their `mechanism` text is clearly different
(ratio < 0.25). Confirmed now requires citation OR `internal_signal` OR
cross-persona agreement within a merged family — not citation AND agreement,
which was the bias-toward-flattery bug the audit flagged. Hedged-language
claims that don't clear the Confirmed bar route to Buried instead of
Inflated. Also renamed `SeverityScore.blind_spot` → `technical` to match the
claims schema's severity axis names.

**Tests:** 137 → 144.

### T2 — Claims-file ingestion + `synthesize` CLI (fixes audit C3)
New `time-travel synthesize claims.json` command: validates against the
vendored schema (`src/time_travel/schemas/claims-v1.json`, via `jsonschema`),
then runs dedupe → classify → confidence → render fully offline. Fails loud
on schema violations, <5 claims, <1 persona, or all-zero severity — raises
`ClaimsValidationError` naming exactly what's wrong rather than rendering a
hollow report. Produces `report.json/html/md` plus a new `exec.html`.

**Tests:** 144 → 154.

### T3 — Confidence bands replace percentages (fixes audit C4)
Rendered output (`report.html`, `report.md`, `exec.md`, `exec.html`) shows
Low(<40)/Guarded(40-60)/Moderate(60-80)/High(>80) plus a one-line driver
("driven by: N confirmed risks, M at Block tier") instead of the raw
percentage. The 0-100 math is unchanged internally; `report.json` still has
`unmitigated_confidence`/`mitigated_confidence` but now also
`confidence_uncalibrated: true` so downstream consumers know not to treat the
numbers as validated.

**Tests:** 154 (existing tests updated, no new ones added).

### T4 — Exec-first HTML output
`report.html` now leads with an exec-summary zone (TL;DR, confidence band,
top-3 ranked risks, the one Buried risk) before a collapsible `<details>`
section holding the full risk table, persona rail, user-POV, mitigations,
and evidence. `exec.html` gets the same ranked content and now enforces the
same 300-word limit as `exec.md` (checked on visible text with tags and
inline `<style>` stripped). Added a hard gate: no line over 2000 characters
in either HTML file.

**Tests:** 154 → 165.

### T5 — Skill rewritten as a thin harness (fixes audit C1/C5)
`SKILL.md` shrank from 198 lines to 105. It no longer contains any
classification/dedup/confidence judgment — that moved to the engine in
T1-T4. The new flow: Phase 0-3 unchanged in spirit (ingest, user-POV,
roster+evidence, persona claims), Phase 4 emits `claims.json` conforming to
the schema, Phase 5 shells out to `time-travel synthesize` (or a vendored
fallback), Phase 6 presents `report.html`.

- `classification.md` and `synthesis.md` moved to `docs/engine/` — they now
  document engine semantics, not skill judgment rules.
- `report-template.md`, `exec-one-pager-template.md`,
  `process-log-template.md`, `example-run.md` deleted — the engine's Jinja
  templates and CLI own all of that now.
- `timeline-prompts.md` rewritten around the claims-v1 field names.
- Default mode is now a single structured response reasoning through all
  personas (was: `--fast` was the opt-in cheap path; now `--deep` opts into
  the expensive parallel-fan-out + rebuttal path).
- Vendored a full copy of `src/time_travel` into
  `harnesses/claude-code/plugins/time-travel/scripts/time_travel/` so the
  engine runs without `pip install` — verified against
  `examples/sample-claims.json` (produces all four artifacts via
  `PYTHONPATH=... python3 -m time_travel.cli synthesize`).
- Bumped `plugin.json` to 0.2.0; verified the packaged zip is a single
  top-level folder with no double-nesting and a schema-valid manifest.

### T6 — Housekeeping
- Pushed all local commits (including the previously-unpushed `a26ec51`) to
  `origin/main`.
- Fixed all 7 pre-existing mypy errors in the provider adapters (typed the
  request/config dicts explicitly, guarded `None` returns) — these are
  exactly the code paths a real-provider smoke test would exercise.
- Left the 18 pre-existing ruff errors in `personas/library.py` and
  `personas/selection.py` untouched — out of scope for this session, not
  files I touched, matches the prior handoff's flagged debt.

---

## Test count

137 (session start) → **165** (session end). `mypy src/` and `ruff check` on
every file touched this session are clean.

---

## Judgment calls (things I decided without an explicit spec line)

1. **Severity axis rename** (`blind_spot` → `technical`) — the claims
   schema's own `$comment` says "adjust the dataclasses, not the schema, if
   they conflict," so I took that literally. This is a real semantic shift
   (blind-spot *detectability* vs. *technical* severity are different
   concepts) — flagging in case the original blind-spot framing was
   intentional and the schema field name was itself the error.
2. **"Specific formulation" and "observable tripwire" aren't engine-checked**
   — classification.md requires these for Confirmed, but they're qualitative
   judgments about phrasing that the engine can't reliably derive from text.
   The engine trusts that claims reaching it were authored specifically (the
   skill's Phase-3 prompt is the actual enforcement point).
3. **"Earliest-firing tripwire" and "most specific change_my_mind"** — true
   temporal/semantic ordering needs judgment the engine doesn't have.
   Implemented as deterministic proxies: first non-empty tripwire in family
   order, longest non-empty change_my_mind text.
4. **Fuzzy-match thresholds** (name similarity 0.6, mechanism-different
   0.25) — picked as reasonable starting points per the audit's suggestion,
   not calibrated against real premortem data. `difflib.SequenceMatcher` on
   sorted tokens stands in for rapidfuzz's `token_sort_ratio` (no new
   dependency); a real rapidfuzz swap later should keep the same threshold
   constants as a starting point but re-validate them.
5. **`plan_text`/`revised_plan` in the claims-driven `Report`** — the
   claims schema carries only `plan.goal` (a ≤400-char summary), not full
   plan text. `synthesize_from_claims` uses `goal` for both and leaves
   `revised_plan` unchanged (no mitigation injection) since there's no full
   text to inject into. If mitigation-injected revised plans are wanted from
   the `synthesize` path, the schema needs a `plan.full_text` field.
6. **`exec.html` is unconditional in `synthesize`** — unlike `run`'s
   `--for-exec` flag, `time-travel synthesize` always writes `exec.html`
   (it's cheap and the audit's resolved architecture treats the exec
   one-pager as the default Cowork output).
7. **Confidence-bar CSS widths** — kept as four static per-band constants
   (20/45/70/95%) rather than the raw score, so the visual bar still shows
   relative magnitude without a report-specific percentage appearing in the
   rendered text.
8. **`<details>` full-report section defaults closed** — read "exec-first"
   literally: the full report is one click away, not shown by default.
9. **Deleted rather than relocated** `report-template.md`,
   `exec-one-pager-template.md`, `process-log-template.md`,
   `example-run.md` — these described the *old* skill-authored output
   format, fully superseded by the engine's Jinja templates and CLI. Unlike
   `classification.md`/`synthesis.md` (which document semantics worth
   keeping as engine docs), these had no remaining reference value.
10. **Vendored `scripts/time_travel/` assumes `jinja2`, `jsonschema`,
    `dataclasses-json`, `marshmallow` are importable** wherever the fallback
    `python3 -m time_travel.cli` runs. Vendoring those pure-Python
    transitive dependencies too (so the bundle needs *zero* external
    packages) was out of scope this session — flagged as the biggest
    remaining risk for the Cowork-sandbox path (see below).
11. **No verified `${CLAUDE_PLUGIN_ROOT}`-equivalent** — SKILL.md's fallback
    invocation tells Claude to substitute the absolute path to its own
    skill directory (which it already knows from having loaded the file)
    rather than relying on an unconfirmed environment variable.

---

## What remains

1. **Real-provider validation** (carried over from the Plan B handoff,
   still not done): run `time-travel run` against actual
   Anthropic/OpenAI/Gemini APIs to confirm the provider adapters' JSON
   parsing survives real model output (prose-wrapped JSON, truncation).
   The provider-adapter mypy fixes in T6 make this safer to attempt, but
   the smoke test itself is still outstanding.
2. **Sandbox verification of the vendored `scripts/` bundle** — confirmed
   working in this session's local `.venv` with all deps installed;
   *not* verified inside an actual Cowork/Claude Code sandboxed Python
   environment where `jinja2`/`jsonschema`/`dataclasses-json`/`marshmallow`
   may not be preinstalled. If they aren't, the fallback path in SKILL.md
   fails and needs either a pure-stdlib rendering fallback or vendoring
   those dependencies too.
3. **rapidfuzz swap** — the audit suggested rapidfuzz or difflib; this
   session used difflib to avoid a new dependency. If matching quality on
   real persona claims turns out weak, swap in rapidfuzz's
   `token_sort_ratio` (same threshold constants as a starting point).
4. **Confidence calibration** — the underlying 0-100 math is still the same
   unvalidated heuristic from Plan B; bands make it presentable but don't
   make it accurate. Calibrating against 5-10 real premortems (per the
   original audit's recommendation) is still open.
5. **`plan.full_text` in the claims schema** — needed if mitigation-injected
   revised plans should come out of the `synthesize` path (see judgment
   call #5).
6. **Plan C** (per the original Plan B spec, unstarted): harness wrappers
   for other CLI targets, install script, GitHub Actions CI, README,
   `scripts/smoke-test.sh`.
7. **Pre-existing ruff debt** in `personas/library.py`/`personas/selection.py`
   (18 line-length/import-order issues) — flagged, not fixed, out of scope.

---

## Related

- [[time-travel-audit]] — the audit this session resolved
- [[time-travel-claim-schema]] — the vendored contract (`schema_version: "1.0"`)
- `docs/engine/classification.md`, `docs/engine/synthesis.md` — engine
  semantics documentation (moved from the skill in T5)
- [[2026-07-05-plan-b-complete-audit-summary]] — the handoff this audit was written against
