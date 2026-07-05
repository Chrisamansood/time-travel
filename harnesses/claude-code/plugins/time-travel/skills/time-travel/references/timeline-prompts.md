# Timeline prompts

The reasoning template for Phase 3, and the exact shape of the `claims` array
the engine expects (see the vendored schema at `scripts/time_travel/schemas/claims-v1.json`
or `docs/handoff/time-travel-claim-schema.json` in the repo).

## Default (fast) mode — one structured response, all personas

Work through this reasoning for **each** persona in the roster, inside a single
response. For each persona, project forward to each horizon and ask: what's
already off at T+3mo? What's broken by T+6mo? What did the plan cost by T+12mo,
even if it "worked"?

For each persona, surface 2–4 plan-specific failure modes (never generic ones
like "scope creep" or "team burnout"). For each failure mode, produce one
entry in the shared `claims` array:

```json
{
  "id": "C1",
  "persona_id": "P1",
  "name": "short, plan-specific noun phrase",
  "mechanism": "HOW it fails — the causal path, not just the symptom",
  "narrative_horizon": "3mo|6mo|12mo|other",
  "severity": {
    "technical": 0, "financial": 0, "trust": 0,
    "user_pain": 0, "ops_load": 0, "strategic": 0
  },
  "likelihood": "low|medium|high",
  "tripwire": "the first OBSERVABLE field signal — never 'things get worse'",
  "change_my_mind": "the specific evidence that would downgrade this risk",
  "citations": ["E1"],
  "internal_signal": "something already visible in the plan itself, if any",
  "hedged_language": false,
  "mitigation": "a concrete action available this week",
  "owner_shape": "role type, never a named individual (see synthesis.md owner-shape list)"
}
```

Rules while filling this in:
- `mechanism` matters as much as `name` — the engine fuzzy-merges claims by
  name AND keeps them separate when mechanisms clearly differ. Two personas
  naming the same symptom for different reasons should stay distinct.
- Cite an evidence-pack item (`E#`) when one supports the claim, or fill
  `internal_signal` when the plan itself already shows the risk, or leave both
  empty and rely on another persona independently raising the same failure —
  the engine treats any of the three as sufficient to confirm a risk.
- Set `hedged_language: true` only when a persona would say this indirectly
  ("there might be some concern about...") rather than name it plainly — that
  routes it to the Buried bucket instead of Inflated.
- Every claim needs a tripwire specific enough that someone could watch for it
  in a dashboard or a support queue. "Users get frustrated" is not a tripwire.

## `--deep` mode — parallel persona dispatch + rebuttal

For board-level or high-stakes plans, dispatch each persona as a separate
parallel `Agent` subagent (`superpowers:dispatching-parallel-agents`) instead
of reasoning through all of them in one response. Each subagent gets the full
plan, its persona definition, the evidence pack, and the Phase-1 user-POV
findings, and returns claims in the same shape as above.

After collecting all persona claims, run one rebuttal round: build a digest of
each persona's top 2 claims (no attribution), send it back to each persona,
and ask where they agree, disagree, or see one failure cascading into another.
Record each reaction as an entry in the claims file's `rebuttals` array:

```json
{"persona_id": "P1", "claim_id": "C4", "stance": "agree|disagree|cascade", "text": "...", "cascade_target": "C7"}
```

`--deep` costs roughly 5x the tokens of the default mode (one call per persona
plus a rebuttal round, vs. one call total) — reserve it for plans a
decision-maker is about to sign off on, not routine checks.
