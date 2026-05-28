# Severity lenses

Risks rarely fail on a single dimension. Technical severity alone misses the failure modes that actually destroy plans — broken trust, quiet support overload, eroded morale. Time Travel scores each failure mode across six lenses.

## The six lenses

Each lens is scored **0–3**. Personas score in Phase 3; the synthesis pass in Phase 4 aggregates them.

### 1. Trust damage

How much does this failure mode erode confidence in the team, product, or organization once it surfaces?

| Score | Meaning |
|---|---|
| 0 | No trust impact. Pure internal issue, invisible externally. |
| 1 | Mild — customers or stakeholders notice and ask polite questions. |
| 2 | Significant — customers or stakeholders question competence or honesty. Recoverable with effort. |
| 3 | Severe — fundamentally undermines the relationship. Some stakeholders won't fully recover their confidence. |

**Example (score 3):** A customer-facing AI claim ("our agent handles 90% of cases") proves false after rollout. The number was always optimistic; admitting it requires retracting public marketing.

### 2. User pain

How much does this failure mode hurt the people who actually use the thing?

| Score | Meaning |
|---|---|
| 0 | No user impact, or improves user experience. |
| 1 | Minor friction — users adapt, mildly annoyed. |
| 2 | Significant friction — workarounds required, users frustrated, support load rises. |
| 3 | Acute pain — users can't complete critical tasks, or are actively harmed (data loss, financial damage, dignity damage). |

**Example (score 3):** A new clinical-workflow tool times out during emergencies, forcing clinicians to fall back to paper at the worst moment.

### 3. Blind-spot risk

How early would the team detect this failure mode? Low score = easy to see. High score = fails silently.

| Score | Meaning |
|---|---|
| 0 | Visible immediately. Smoke alarms go off. |
| 1 | Visible within days or in the first review cycle. |
| 2 | Visible only after weeks; needs a specific metric to be tracked. |
| 3 | Fails silently for months. The team only realizes when the damage is done — often via an external signal. |

**Example (score 3):** A subtle data-quality drift that produces plausible-looking AI outputs which are wrong; nobody notices until a customer escalates with evidence.

### 4. Ops load

How much ongoing operational capacity does this failure mode consume?

| Score | Meaning |
|---|---|
| 0 | No operational burden. |
| 1 | Mild — a few extra tickets or alerts per week. |
| 2 | Significant — a recurring weekly fire that consumes a specific team member's time. |
| 3 | Severe — saturates a team or function. Causes burnout, attrition, or reprioritization away from forward work. |

**Example (score 3):** A new AI customer-service tier escalates so much to humans that the support team spends more time on handoffs than before automation.

### 5. Financial

How much direct financial damage does this failure mode cause?

| Score | Meaning |
|---|---|
| 0 | Negligible. |
| 1 | Mild — a one-off cost; absorbed inside the budget. |
| 2 | Material — large enough to require explanation to finance, board, or budget committee. |
| 3 | Severe — affects the company's quarterly results, requires a write-down, or triggers a covenant. |

**Example (score 3):** A vendor lock-in turns out to be more expensive than projected and the contract is non-cancellable.

### 6. Strategic

How much does this failure mode undermine the bigger strategic bet the plan is part of?

| Score | Meaning |
|---|---|
| 0 | No strategic impact. Tactical issue only. |
| 1 | Delays a tactical milestone but the strategy stays intact. |
| 2 | Forces a meaningful pivot or repositioning. |
| 3 | Invalidates the strategic premise — the org has to question whether the larger bet was right. |

**Example (score 3):** A multi-year AI transformation program loses its anchor customer because the first rollout damaged trust; the strategy needs rethinking.

## Computing a total severity score

For a single failure mode, sum the six lenses (max 18). This gives a comparable severity number.

However: **the lenses are not equal**. Don't treat the sum as the whole story. A failure mode that scores 3 on trust-damage and 0 elsewhere is often worse for a plan than one that scores 1 across the board, because trust damage is hard to recover.

In Phase 4 synthesis:
- Rank risks first by **count of 3s** (any 3 is significant)
- Then by sum
- Then by likelihood (High > Medium > Low) as a tiebreaker

## Combining persona scores

When multiple personas score the same failure-mode family in Phase 3:

- For each lens, take the **max** across personas (worst-case framing — premortems should be honest about ceilings, not averages)
- For likelihood, take the **mode** (most common rating); if tied, take the higher
- Record the inter-persona variance in the process log — large variance means the personas saw different aspects of the same failure

## What to push back on

If a persona scores a risk:
- **All zeros** — they don't think it's a risk. Don't include it.
- **All threes** — they may be exaggerating; check the citation. If unsupported, downgrade.
- **High trust-damage but score 0 on user_pain and ops_load** — suspicious. Trust damage usually shows up via user pain or ops load first. Ask the persona to specify the mechanism.
