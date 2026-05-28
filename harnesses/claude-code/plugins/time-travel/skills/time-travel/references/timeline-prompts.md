# Timeline prompts

The exact prompt each persona subagent receives in Phase 3 (parallel fan-out) and Phase 3.5 (rebuttal round).

## Phase 3 — Per-persona dispatch prompt

Substitute the variables in `{braces}` before sending. Each persona gets this prompt as the body of a single `Agent` call.

```
You are {persona_name}.

Your POV: {persona_pov}
You care about: {persona_cares_about}
You tend to overlook: {persona_overlooks}

You're going to time-travel into the future of the plan below. You don't trust it — that's your job. Project yourself forward to three points in time and report honestly what you observe.

---

THE PLAN:
{full_plan_text}

---

USER-POV CONTEXT (what the intended users wanted):
{user_pov_summary_from_phase_1}

---

REAL-WORLD ANALOGUE CASES YOU SHOULD KNOW ABOUT:
{evidence_pack — 3 to 5 cases, each: source, what happened, why relevant}

---

YOUR TASK

Write three first-person narratives, one at each horizon. Each narrative is 100–200 words, present tense, as if you're standing inside the plan's reality at that point in time.

- {horizon_1} (default: T+3 months) — Early signals. What's already off? What did the team underestimate? Who's quietly unhappy?
- {horizon_2} (default: T+6 months) — Mid-game. What promises have broken? What workarounds has the team invented? What's eroding trust?
- {horizon_3} (default: T+12 months) — Mature outcome. Did the plan deliver what it promised? If not, why not? If yes, what came at hidden cost?

Then list 3–5 specific failure modes you've identified. For each:

- **Name** — one short noun phrase, plan-specific (NOT generic like "scope creep")
- **Severity scores** — score 0 to 3 on each of these six lenses:
  - trust_damage (0=none, 3=severely undermines confidence in the team/product)
  - user_pain (0=none, 3=actively painful or harmful for users)
  - blind_spot (0=visible early, 3=fails silently and slowly)
  - ops_load (0=no operational cost, 3=consumes ongoing capacity)
  - financial (0=trivial, 3=material financial damage)
  - strategic (0=tactical only, 3=undermines the bigger strategic bet)
- **Likelihood** — Low / Medium / High
- **Tripwire** — the first observable signal in the field. Be specific. ("Support ticket volume on topic X rises >15% week over week", not "user complaints increase")
- **What would change my mind** — the specific evidence that would let me downgrade or dismiss this risk
- **Citation** — which analogue case, which user-POV finding, or which line of the plan supports it

OUTPUT FORMAT (return JSON only — no preamble, no commentary):

```json
{
  "persona": "{persona_name}",
  "narratives": {
    "{horizon_1}": "...",
    "{horizon_2}": "...",
    "{horizon_3}": "..."
  },
  "failure_modes": [
    {
      "name": "...",
      "severity": {
        "trust_damage": 0,
        "user_pain": 0,
        "blind_spot": 0,
        "ops_load": 0,
        "financial": 0,
        "strategic": 0
      },
      "likelihood": "Low|Medium|High",
      "tripwire": "...",
      "what_would_change_my_mind": "...",
      "citation": "..."
    }
  ]
}
```

DO NOT:
- Write generic risks that could apply to any plan ("team burnout", "scope creep", "stakeholder misalignment"). Only risks specific to THIS plan.
- Pretend you have specialist knowledge outside your persona's lane. If you don't know it, don't write it.
- Hedge. Your job is to surface failure modes confidently. Politeness here is a process failure.
- Echo what the plan already says. You're projecting forward, not summarizing.
- Write more than 5 failure modes. If you have more, pick the 5 most specific to this plan.
```

## Phase 3.5 — Rebuttal-round prompt

After collecting all persona outputs in Phase 3, build a digest (no attribution): for each persona, list their top 2 failure-mode names + tripwires. Strip the persona name.

Then dispatch each persona again with this prompt:

```
You are {persona_name} — same POV as before.

You've already written your premortem. Now you're reading what the other personas surfaced (names redacted). Your job: rebut or extend.

OTHER PERSONAS' TOP FINDINGS (no attribution):
{digest_of_other_personas}

YOUR TASK

For the findings above, answer briefly:

1. **Agreements** — Which findings would you also have raised? Which strengthen your own narrative?
2. **Disagreements** — Which findings are weak or wrong from your POV? Be specific about why.
3. **Cascades** — Do any of these findings, in combination, produce a worse failure than any single one alone? Describe the chain.
4. **Blind spots** — Reading these, is there a failure mode that none of you (including you) captured? Add it now (same format as Phase 3).

OUTPUT FORMAT:

```json
{
  "persona": "{persona_name}",
  "agreements": ["finding name + brief reason", "..."],
  "disagreements": [{"finding": "...", "why_weak": "..."}],
  "cascades": [{"chain": "finding A → finding B → outcome", "severity_uplift": "Low|Medium|High"}],
  "new_failure_mode": {  // optional; null if none
    "name": "...",
    "severity": {...},
    "likelihood": "...",
    "tripwire": "...",
    "what_would_change_my_mind": "...",
    "citation": "..."
  }
}
```

DO NOT:
- Re-list everything from your Phase 3 output.
- Agree with all findings — that signals the roster lacks diversity. Find real disagreement.
- Pretend a cascade exists when it doesn't. Only flag a cascade if the chain is genuinely tighter than the individual links.
```

## Notes on `--fast` mode

When `--fast` is set, skip the parallel dispatch entirely. Run a single main-thread prompt that asks Claude to roleplay all chosen personas in sequence, producing the same JSON schema. Skip Phase 3.5 (rebuttal round). The output will be flatter — personas in a single context tend to converge in tone — but the structure is preserved.
