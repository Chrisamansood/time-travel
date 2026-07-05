---
name: time-travel
description: Run a multi-agent premortem on a plan — stakeholder personas project failure modes across T+3/6/12 months, and the time-travel engine classifies them into a Confirmed/Inflated/Buried report. Trigger on "/time-travel:run", "premortem", "stress test this plan", "what could go wrong", "kill this plan if you can", or adversarial review of an AI-generated plan.
---

# Time Travel

A premortem harness. You do the persona reasoning; the `time-travel` engine
(Python, vendored in `scripts/`) does the deterministic classification, confidence
scoring, and report rendering. You never classify or score a report by hand —
that logic lives in the engine so results are consistent and testable. See
`docs/engine/classification.md` and `docs/engine/synthesis.md` in the repo if
you want to understand *why* the engine classifies the way it does.

## Invocation contract

```
/time-travel:run [source] [--deep] [--horizons LIST] [--output PATH]

source       File path, quoted plan text, or omitted (auto-detect: latest
             file in ./plans/, then ~/.claude/plans/, then the last
             substantial assistant message, then ask the user to paste).
--deep       Parallel persona subagents + a rebuttal round (~5x the cost
             of the default). Reserve for board-level, high-stakes plans.
--horizons   Override the default 3mo,6mo,12mo.
--output     Override the default ./time-travel-reports/.
```

Default mode reasons through all personas in one response — cheap, fast,
good for routine checks. If unsure which mode to use, ask the user once.

## The flow

**Phase 0 — Ingest.** Resolve and read the plan. Extract goal, timeline,
stakeholders, source type (human-authored vs. AI-generated). If there's not
enough structure to reason about, ask up to 2 clarifying questions.

**Phase 1 — User-POV + blind spots.** ~150 words, main thread: what did
users expect, what would they forgive, what would feel untrustworthy, what
complaints are predictable? Then name 1-3 `blind_spot_candidates` — risks
everyone privately knows about but the plan doesn't name (see
`references/anti-patterns.md` for what these look like).

**Phase 2 — Roster + evidence.** Pick 5-7 personas from
`references/persona-library.md`: 2-3 universal, 3-4 domain-specific, plus the
AI-Optimism persona if the plan is AI-generated. Run 3-5 web searches per
`references/grounding.md` for real analogue failures; keep an evidence pack
(`E1`, `E2`, ... with title/url/what_happened/why_relevant).

**Phase 3 — Persona claims.** Follow `references/timeline-prompts.md`. Default
mode: reason through every persona in this one response. `--deep`: dispatch
each persona as a parallel `Agent` subagent, then run the rebuttal round.
Score each claim on the six lenses in `references/severity-lenses.md`.

**Phase 4 — Emit `claims.json`.** Assemble everything into one JSON file
matching the schema at `scripts/time_travel/schemas/claims-v1.json`:
`schema_version`, `plan`, `mode`, `user_pov`, `blind_spot_candidates`,
`evidence`, `personas`, `claims`, and `rebuttals` (deep mode only). Write it
to a temp path (e.g. `./time-travel-reports/claims.json`).

**Phase 5 — Synthesize.** Run the engine — never hand-classify:

```bash
time-travel synthesize ./time-travel-reports/claims.json --output ./time-travel-reports
```

If that command isn't found, the pure-function engine is vendored alongside
this skill at `scripts/time_travel/` (sibling of this SKILL.md's own
directory). Fall back to it using the absolute path you already know from
having loaded this file:

```bash
PYTHONPATH="<absolute path to this skill's folder>/../../scripts" \
  python3 -m time_travel.cli synthesize ./time-travel-reports/claims.json --output ./time-travel-reports
```

If synthesis fails (schema violation, too few claims, all-zero severity), the
engine's error message names exactly what's wrong — fix the claims file and
re-run. Don't work around the failure by writing your own report.

**Phase 6 — Present.** Open `report.html` from the printed output directory
(exec summary + full collapsible detail). Print the TL;DR, confidence band,
and artifact paths to chat.

## Anti-patterns

See `references/anti-patterns.md` in full before Phase 3. The short list:
generic plan-agnostic risks, treating technical severity as the only lens,
zero Buried risks (almost every plan has one), vague tripwires, hedging
instead of naming a risk plainly, letting every persona agree.

## Tools used

- `WebSearch` — evidence pack (Phase 2).
- `Agent` (`superpowers:dispatching-parallel-agents`) — `--deep` mode only (Phase 3).
- `Write` — the claims.json file (Phase 4).
- `Bash` — invoking the engine (Phase 5).

## References (progressive disclosure — load per phase, not all at once)

- `references/persona-library.md` — roster + selection heuristics (Phase 2)
- `references/severity-lenses.md` — the six severity dimensions (Phase 3)
- `references/timeline-prompts.md` — claim-authoring template + schema shape (Phase 3)
- `references/grounding.md` — web-search heuristics, AI-pattern detection (Phases 0, 2)
- `references/anti-patterns.md` — common failure modes for this skill (read before Phase 3)
