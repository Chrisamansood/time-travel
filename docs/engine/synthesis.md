# Synthesis

The main-thread work in Phase 4. Collapses persona outputs into a coherent report.

Five sub-steps:

1. Deduplicate failure modes into families
2. Classify (see `classification.md`)
3. Pick top 5–7 risks
4. Write the revised plan
5. Compute revised confidence

This file covers steps 1, 3, 4, and the confidence math. Step 2 lives in `classification.md`.

---

## 1. Deduplication

Personas in Phase 3 will surface overlapping failure modes from different angles. Don't list them separately — collapse into families.

### Process

1. **Collect** all failure modes from all personas (typically 15–35 modes after a 5-persona fan-out).
2. **Group** modes that describe the same underlying failure, even if the framing differs.
   - "Support team can't keep up with escalations" (Support-Lead) + "Users frustrated by 24-hour response times" (Frustrated-End-User) + "Ops on-call gets paged for things support should handle" (Ops-Engineer) → one family.
3. **Pick the strongest formulation** as the family's canonical name (usually the most specific and observable).
4. **Merge severity scores** using the per-lens max (see `severity-lenses.md`). Record which personas contributed.
5. **Merge tripwires** by selecting the earliest-firing one (the leading indicator wins).
6. **Merge "what would change my mind"** by selecting the most specific (or combining if they're complementary).

### When to keep modes separate (don't over-dedupe)

- If two modes have **different tripwires** that fire at different times, keep them separate even if the eventual outcome is similar.
- If two modes are caused by **different mechanisms** (e.g., "system fails because vendor SLA gap" vs "system fails because internal capacity gap"), keep them separate — the mitigations differ.
- If one persona's framing reveals a meaningfully different stakeholder impact, keep it visible.

---

## 3. Picking the top 5–7 risks

After classification (`classification.md`), select the top risks for the report's main table.

### Ranking

Within Confirmed risks:

1. **All Block-tier risks** are included (these are non-negotiable for the table).
2. **Patch-fast risks** ranked by:
   - Count of severity-lens 3s (any lens scoring 3 counts as 1)
   - Then total severity sum (0–18)
   - Then likelihood (High > Medium > Low)
3. **Monitor risks** included only if total count < 7 and they meaningfully differ from already-listed risks.

### Edge cases

- **More than 7 Block-tier risks** — the plan is over-scoped or under-defined. Flag in the TL;DR: *"This plan has N blocking risks. Reconsider scope or decompose before proceeding."* Include all of them anyway.
- **Fewer than 3 Confirmed risks** — either the plan is genuinely low-risk or the personas were too aligned. Re-examine the rebuttal round for missed cascades and re-examine the user-POV pass for surfaced concerns.

---

## 4. The revised plan

Take the original plan and fold the mitigations in. **Inject, don't rewrite.**

### Rules

- **Preserve structure.** If the original plan has phases, milestones, or bullets, keep them. Inject mitigations as sub-bullets, footnotes, or annotations.
- **Mark injections clearly.** Use a consistent prefix or italics so the reader can see what's new. Suggested format: `_[Mitigation for Risk #N: ...]_`
- **Don't change tone.** If the original is corporate, keep it corporate. If it's casual, keep it casual.
- **Address Block risks first.** Each Block risk should have a corresponding injection in the relevant phase of the plan.
- **Don't address every Confirmed risk inline.** Patch-fast and Monitor risks belong in the report's mitigation section, not stuffed into the plan body. The revised plan is for things that change the work, not for things that get tracked.
- **Add a "Pre-flight checks" section at the top** if any Block risks need resolution before kickoff (e.g., "Block risk #2 — vendor SLA gap — must be renegotiated or backstopped before Phase 1 starts").

### What good injection looks like

Original:
```
Phase 2: Roll out to all customers in Q3.
```

After injection (for a Block risk about regional regulatory differences):
```
Phase 2: Roll out to all customers in Q3.
  _[Mitigation for Risk #1: EU customers excluded until AI Act compliance review completes;
  flagged separately in EU rollout addendum. Decision date: end of June.]_
```

---

## 5. Revised confidence math

Two numbers go into the report: **unmitigated confidence** (X%) and **mitigated confidence** (Y%). They anchor the conversation.

This math is heuristic, not Bayesian. The goal is a defensible single number, not a precise forecast.

### Step 1 — Establish a baseline

If the plan states a confidence ("we expect to hit 90% by Q3"), use that as the starting baseline.

Otherwise:
- Default baseline = **65%** for a "competently scoped, plausibly resourced" plan
- Adjust down if the plan compresses multi-quarter work into one quarter
- Adjust down if the plan depends on capabilities or relationships that don't yet exist
- Adjust up if the plan has prior successful runs in the same org
- Sanity bounds: 30% (very ambitious / unproven) to 80% (incremental / proven approach)

### Step 2 — Risk-score the Confirmed-Block + Patch-fast risks

For each:

```
risk_score = (severity_sum / 18) × likelihood_weight

where likelihood_weight = High: 1.0 | Medium: 0.6 | Low: 0.3
```

Cap each risk_score at 0.25 (no single risk reduces confidence by more than 25 points).

### Step 3 — Unmitigated confidence

```
unmitigated = baseline × ∏ (1 − risk_score_i)   for the top 5 risks
```

(Multiplicative — risks compound, but capped contribution prevents zero.)

Round to nearest 5. Display as `XX%`.

### Step 4 — Mitigated confidence

For each of the top 3 risks (by risk_score), apply the mitigation:

```
mitigated_risk_score_i = risk_score_i × (1 − mitigation_effectiveness)

where mitigation_effectiveness:
  • 0.7 if the mitigation is concrete, actionable this week, and clearly addresses the mechanism
  • 0.4 if the mitigation is concrete but slow or partial
  • 0.2 if the mitigation is aspirational ("we should consider…")
```

Then recompute with mitigated scores for the top 3 (use original scores for the rest).

```
mitigated = baseline × ∏ (1 − mitigated_risk_score_top_3) × ∏ (1 − risk_score_rest)
```

Round to nearest 5. Display as `YY%`.

### Step 5 — Sanity check

- `mitigated` should be **higher** than `unmitigated` by at least 5 points. If not, the mitigations aren't strong enough — re-write them.
- If `mitigated − unmitigated > 30`, the mitigation effectiveness is being over-claimed. Recalibrate.
- Both numbers should round to multiples of 5 in the report (precision implies false rigor).

---

## Owner shapes (vocabulary for "who would own this")

Use these labels when filling the "Owner shape" column. **Never name specific individuals** — the report goes to external audiences too.

- Executive Sponsor
- Product Manager
- Engineering Lead
- Operations Lead
- Customer Success Lead
- Support Lead
- Sales Lead
- Finance / FP&A
- Compliance / Legal
- Communications
- HR / People Ops
- Vendor Owner (third-party relationship)
- Data Owner
- Security Owner
- Risk / Audit

Pick the **lowest-rank role that has the authority to act**. If a mitigation requires executive air cover, list both: "Engineering Lead (Executive Sponsor)".
