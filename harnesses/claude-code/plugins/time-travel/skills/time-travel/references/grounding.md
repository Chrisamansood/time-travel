# Grounding

Two jobs in one document:

1. **Web search heuristics** — how to find real-world analogue failures for the evidence pack (Phase 2)
2. **AI-pattern detection** — how to decide whether to auto-include the AI-Optimism persona (Phase 0)

---

## Part 1 — Web search heuristics for analogue evidence

The goal is **3–5 real-world cases** where something *like* this plan was tried and either failed, partially failed, or required significant course-correction. The cases prime the personas with concrete reference points.

### Build the queries

For each plan, extract:

- **Domain** — industry or vertical (e.g., telecom, healthcare, retail, fintech, internal-tools)
- **Core action** — the verb of the plan (rollout, migrate, replace, automate, launch, restructure)
- **Object** — what the action operates on (customer service, claims processing, ERP, sales enablement)
- **Approach** — distinguishing mechanism (AI agent, low-code, vendor consolidation, in-house build)

Compose 3–5 targeted queries from these. Vary the angle:

1. **Direct analogue** — `<domain> <core action> <object> <approach> failure`
2. **Named-precedent** — search for known cases: `Klarna AI customer service rollback`, `McDonald's IBM AI drive-through failure`, `Air Canada chatbot lawsuit`, etc.
3. **Counter-claim** — `<approach> didn't work` or `<approach> overpromised`
4. **Specific stakeholder reaction** — `<object> rollout employee backlash`, `<object> customer complaints AI`
5. **Regulator angle** — `<domain> AI compliance enforcement` (if regulated)

### What to look for in a result

A good analogue case has:

- A **named entity** (company, organization) — anonymous case studies are too easy to confabulate
- A **specific mechanism** of failure (not "it didn't work" — *why* it didn't work)
- A **post-mortem signal** — an article, a tweet thread, an analyst note, an earnings call mention
- **Recency** — within ~3 years is most relevant; older cases need a "why this still matters" justification

Reject results that are:
- Press-release rewrites without independent reporting
- Generic "5 reasons AI projects fail" thinkpieces
- Vendor-authored case studies (too sanitised)
- Conference talks without independent corroboration

### Build the evidence pack

For each of the 3–5 retained cases, write a 2–4 sentence brief:

```
**[Source title]**(url) — <when>, <who>: <what happened> <why relevant to this plan>
```

Example:

```
**[Klarna walks back AI-only customer service](https://www.bloomberg.com/...)** — May 2025, Klarna reversed its 2024 announcement that AI had replaced 700 customer service roles; cited quality issues and rehired staff. Relevant because this plan similarly assumes a high deflection rate without a fallback design.
```

Aim for the whole pack to fit in ~600 tokens. Personas in Phase 3 receive the pack verbatim.

If 3 strong analogue cases can't be found, fall back to **adjacent-domain** cases (same approach, different industry) — still better than no grounding. Note the adjacency in the brief.

---

## Part 2 — AI-pattern detection (when to auto-include AI-Optimism persona)

If the user passes `--ai-source`, always include the AI-Optimism persona. Otherwise, run these heuristics on the plan source and include the persona if **3 or more** of the patterns below fire.

### Pattern 1 — Vague success criteria

The plan promises outcomes without specifying how they'd be measured.

**Triggers:**
- "Significant", "transformational", "best-in-class", "leading-edge", "next-generation"
- Outcomes stated as adjectives, not metrics ("improved customer satisfaction" not "+15 NPS")
- Goals that can't be falsified

### Pattern 2 — Buzzword density

The plan reads like a corpus of marketing fluff.

**Triggers:**
- High frequency of: "leverage", "synergy", "seamless", "holistic", "robust", "end-to-end", "enterprise-grade", "scalable", "innovative", "cutting-edge", "future-proof"
- Three or more in close proximity is a strong signal

### Pattern 3 — Suspiciously round numbers

The plan quotes outcomes in round, evenly-spaced numbers.

**Triggers:**
- "10x", "40% reduction", "50% improvement", "90% deflection", "save millions"
- Multiple numbers in the plan, all ending in 0 or 5
- Forecasts without an estimation method named

### Pattern 4 — Generic recommendations

The plan reads like it could apply to any company in any industry.

**Triggers:**
- No mention of named systems, named teams, named customers, or specific organizational context
- Recommendations identical to what one would write for a generic Fortune 500
- No reference to the company's prior failed attempts or specific constraints

### Pattern 5 — Missing trade-offs

The plan presents a path forward with no honest discussion of what's being given up.

**Triggers:**
- No "risks" section, OR a risks section that lists only easily-mitigated risks
- No discussion of opportunity cost
- No alternatives considered or named
- No mention of who or what loses if this plan ships

### Pattern 6 — Confidence without evidence

The plan asserts conviction in outcomes without supplying the basis.

**Triggers:**
- "We will", "this will deliver", "expected to achieve" — without citation
- Forecasts with no model, no analogue, no pilot data
- Phrasing like "industry-standard payback" without citing the industry standard

### Pattern 7 — Plurals without specifics

The plan refers to "stakeholders", "customers", "teams" generically.

**Triggers:**
- "Engage stakeholders" / "align teams" / "enable customers" without naming which
- Roles described in generic title-case ("the Account Manager") rather than specific people or named groups

### Pattern 8 — Training-data averages

The plan's recommendations resemble what an average competent consultant would say for an average company — the median answer, not the *right* answer for this org.

**Triggers:**
- Recommendations that match the consensus blog-post advice on the topic
- Phases named like generic playbooks ("Phase 1: Discover, Phase 2: Design, Phase 3: Deliver")
- Structure that mirrors common corporate-template formats

---

### Acting on the detection

If `--ai-source` is set, OR 3+ patterns fire:

1. Include the **AI-Optimism Auditor** persona in the Phase 2 roster.
2. In the report's `frontmatter`, set `ai_source: true`.
3. In the TL;DR, lead with a one-line note: *"This plan appears AI-authored. Treat its claims as hypotheses, not commitments, until validated."*
4. The AI-Optimism persona's outputs get **first priority** in the rebuttal-round digest — its findings are usually the ones the human team has been least likely to consider.

If fewer than 3 patterns fire and `--ai-source` is not set: don't include the persona. False positives waste a slot in the roster.
