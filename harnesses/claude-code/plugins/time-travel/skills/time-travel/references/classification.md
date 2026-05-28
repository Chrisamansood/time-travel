# Classification: Confirmed / Inflated / Buried

In Phase 4, every deduplicated failure-mode family gets classified into one of three buckets, and Confirmed risks get an additional urgency tier. This file defines the buckets, the criteria, and the decision flow.

## The three buckets

### Confirmed

A real, evidence-backed risk. Ignoring it would be negligent.

**Criteria — all must hold:**
- At least one persona surfaced this risk with a specific, plan-relevant formulation (not generic).
- The risk has either:
  - An analogue case in the evidence pack (a similar plan that failed for a similar reason), OR
  - An internal signal already visible in the plan (e.g., the plan depends on a vendor whose roadmap is unknown, the plan assumes user behaviour we have no data for, the plan compresses a multi-quarter change into one quarter), OR
  - Cross-persona agreement (two or more personas raised closely related concerns)
- The tripwire is observable, not speculative.
- The "what would change my mind" answer is itself specific — you can imagine someone bringing that evidence.

**Examples:**
- "Vendor SLA does not cover the failure mode the plan depends on" (specific, evidenced by reading the contract)
- "Compliance review hasn't started and the regulation takes effect in 60 days" (specific, calendar-evidenced)
- "Three personas independently surfaced the same data-quality concern" (cross-persona agreement)

### Inflated

A risk that sounds dramatic on first read but downgrades on inspection. Either the likelihood is genuinely low, or the impact would be small/recoverable.

**Criteria — at least two must hold:**
- The risk is hypothetical or speculative without supporting evidence.
- The likelihood is low (e.g., needs multiple unlikely things to align).
- The impact, if it occurred, would be small or quickly recoverable.
- The persona who raised it is operating outside their lane.
- A specific structural feature of the plan (or the org) makes this risk implausible.

**Examples:**
- "A competitor could copy this in 6 months" — but their roadmap is public and they're focused elsewhere.
- "Users will hate the new UI" — but usability testing showed satisfaction; this is general anxiety, not evidence.
- "The market might shift" — vague, unfalsifiable; no specific shift named.

**How to handle:** Don't delete Inflated risks — record them with a one-line "why downgraded" note. Visible Inflated risks signal a rigorous process and pre-empt the "what about X?" question in review.

### Buried

A risk everyone is aware of but no one wants to say out loud. The Confirmed/Inflated split is about evidence; the Buried bucket is about *politics*.

**Signals that a risk is Buried:**
- A persona raised it, but in indirect or hedged language (e.g., "there might be some concern about leadership alignment" rather than "the head of sales is openly skeptical and hasn't been included")
- The risk is named in the rebuttal round disagreements but absent from the original plan's "risks" section
- The plan goes out of its way *not* to name a specific person, vendor, or political dynamic that's structurally obvious
- The risk involves: power dynamics, individual accountability, vendor relationships that someone defended internally, a sunk-cost commitment, a CEO-favored direction that customers haven't validated, an "everyone knows" workaround that no one writes down

**Buried risks frequently include:**
- "The technical lead disagrees with this direction and has been disengaged"
- "The CEO's pet feature is in the plan but no customer has asked for it"
- "We are dependent on a vendor we've already had to firefight twice this year"
- "The team is being asked to deliver two incompatible priorities and no one's willing to choose"
- "The previous version of this plan failed for the same reason and we haven't said so"

**How to handle:** Name the Buried risk explicitly in the report. For each Buried risk:
- Write the risk in clear, blame-free language.
- Note *why* it's being avoided (politics, power, sunk cost, etc. — without naming individuals).
- Suggest a way to surface it constructively in conversation (e.g., "Ask: which version of this plan have we tried before, and what did we learn?").

**Important:** If your synthesis produces zero Buried risks, this is a process failure, not a clean bill of health. Re-examine the rebuttal round, the hedged language, and the user-POV pass for what's been avoided. Almost every plan has at least one Buried risk.

## Decision flow

For each deduplicated failure-mode family:

```
Is there specific, plan-relevant evidence or cross-persona agreement?
├── YES → Is the tripwire observable and the "what would change my mind" specific?
│        ├── YES → CONFIRMED (proceed to urgency tier)
│        └── NO → Tighten the formulation; reconsider
└── NO  → Is this risk being hedged or talked around rather than named?
         ├── YES → BURIED (write it plainly; suggest how to surface)
         └── NO → Is the likelihood low or the impact small/recoverable?
                  ├── YES → INFLATED (record with "why downgraded")
                  └── NO → Likely a Confirmed risk with weak articulation; tighten
```

## Urgency tiers (for Confirmed risks only)

Every Confirmed risk gets exactly one urgency tier.

### Block

The risk must be resolved (or have a concrete mitigation plan with assigned ownership and a deadline) **before** the plan proceeds. Ignoring it would invalidate the plan.

**Use when:**
- The risk is legally or contractually disqualifying (e.g., compliance not met by deadline)
- The risk has no graceful failure mode (e.g., irrecoverable data loss)
- The risk affects a hard dependency without which downstream phases can't start
- The risk is currently materializing (the tripwire is already firing)

**Example:** "EU AI Act compliance documentation isn't started and the deadline is 60 days before launch."

### Patch-fast

The risk doesn't block the plan from starting, but must be addressed within the **first window after launch** (typically 0–3 months post-launch, or the first review cycle).

**Use when:**
- The risk's impact compounds over time but is small at launch
- A workaround exists for the launch window
- The risk materializes only with scale, and scale takes time to arrive

**Example:** "Support team isn't sized for the predicted ticket volume from week 6 onward."

### Monitor

The risk is real but doesn't require active mitigation. It needs a tripwire and a review cadence.

**Use when:**
- The likelihood is medium but the cost of preemptive mitigation is high
- The risk depends on external events outside your control
- Mitigation would over-rotate; better to watch and respond

**Example:** "A specific competitor might announce a similar feature. We'll know within 6 months; if they do, we'll respond then."

## Selecting the top risks for the report

Don't list every Confirmed risk in the main "top risks" table. Pick **5–7** for the user-facing top-risks section using this rank:

1. All Confirmed-Block risks (these are non-negotiable)
2. Then Confirmed-Patch-fast risks, ranked by severity × likelihood
3. Then Confirmed-Monitor risks only if there's room

If you end up with more than 7 Block risks, the plan likely needs decomposition before any premortem can help — flag this explicitly in the TL;DR.

Always list **all** Inflated and Buried risks in their respective sections, regardless of count.
