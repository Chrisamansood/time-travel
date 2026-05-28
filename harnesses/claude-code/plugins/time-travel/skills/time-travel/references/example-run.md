# Example run

A worked walkthrough on a synthetic, plausible plan. Use this for calibration — both for the kind of plan Time Travel handles well, and for the tone and depth the artifacts should hit.

The plan below is synthetic and the analogue cases are real public examples; nothing here references any specific customer or internal initiative.

---

## The synthetic input plan

```
# Project: AI-First Customer Service Rollout
# Owner: Sarah K., VP Customer Experience
# Approved by: Exec team, Q1 review

## Goal
Deploy an AI customer service agent to all customer-facing inquiries within
6 months. Target: 90% deflection rate (cases resolved without human escalation),
40% reduction in customer-service operating cost, no degradation in CSAT.

## Phases
Phase 1 (Month 1-2): Vendor selection and integration with existing CRM.
Phase 2 (Month 3-4): Pilot with two largest customer segments.
Phase 3 (Month 5-6): Full rollout to all customer-facing channels.

## Why now
Customer-service costs grew 22% last year. Industry leaders have deployed
similar AI agents and report significant savings. Our CRM vendor has a
ready-to-use AI module. We need to keep pace.

## Success criteria
- 90% deflection in Phase 3
- 40% lower OpEx by end of year
- CSAT unchanged

## Risks
- Integration with legacy CRM may take longer than expected. Mitigation:
  early vendor engagement.
- Some customers may prefer human agents. Mitigation: clear opt-out path.
```

## AI-pattern detection — what fires

Running the heuristics in `grounding.md`:

1. **Vague success criteria** — partial ("significant savings", "industry leaders") ✓
2. **Buzzword density** — low; this plan is relatively plain. ✗
3. **Suspiciously round numbers** — yes (90%, 40%, 6 months) ✓
4. **Generic recommendations** — partial (the rationale "keep pace" is generic) ✓
5. **Missing trade-offs** — yes (no honest discussion of what's given up) ✓
6. **Confidence without evidence** — yes ("industry leaders ... report significant savings" — no citation) ✓
7. **Plurals without specifics** — yes ("industry leaders", "customer segments") ✓
8. **Training-data averages** — yes (the phasing reads like a template) ✓

Count: 7 patterns fire. **AI-Optimism Auditor persona is auto-included.** Frontmatter `ai_source: true`.

---

## Roster selection

Universal personas (2):
- Skeptical-Money
- Frustrated-End-User

Domain personas (4):
- Support-Lead — they own the queue this plan tries to shrink
- Customer-Success-Manager — they own renewal risk on top accounts
- Ops-Engineer — they own the integration runtime
- Vendor/Partner-PM — the CRM vendor's roadmap is load-bearing

Conditional persona (1):
- **AI-Optimism Auditor** — 7 AI-patterns fired

Roster size: 7. Considered but dropped: Regulator (no clear regulatory exposure beyond data handling, which is captured by Ops-Engineer); Sales-Rep (renewal narrative captured by Customer-Success-Manager).

## Evidence pack (3 real analogues)

```
[Klarna walks back AI-only customer service](https://www.bloomberg.com/...) —
May 2025, Klarna reversed its 2024 announcement that AI had replaced 700
customer-service roles; cited quality issues and rehired staff. Relevant:
this plan similarly assumes high deflection without a documented fallback.

[Air Canada chatbot ordered to pay damages](https://www.bbc.com/...) — Feb 2024,
a Canadian tribunal held Air Canada liable for incorrect information given by
its AI chatbot about a bereavement fare. Relevant: this plan doesn't address
who's accountable when the AI gives wrong information.

[McDonald's ends IBM AI drive-through partnership](https://www.cnbc.com/...) —
June 2024, McDonald's ended its IBM AI drive-through trial after viral
videos of failures; cited rollout pace and quality. Relevant: the rollout
pace ambition in this plan (6 months to full deployment) mirrors a pattern
seen in failed AI-customer rollouts.
```

---

## Sample Phase 3 output — one persona

### AI-Optimism Auditor

**T+3mo:** Two months in. The vendor's standard module is integrated but it can't access three of the most-used internal knowledge bases. The plan promised 90% deflection; current pilot data shows 35%. The phrase "ramping" is appearing in internal updates. The team has stopped quoting the 90% number aloud but it's still in the slide deck for the board.

**T+6mo:** The full rollout has shipped. Real deflection is sitting at 48%. The team has pivoted the framing: "deflection" now includes cases where the AI answered but the customer still escalated within 24 hours. The 40% cost-reduction number is being defended via headcount that hasn't yet been laid off — paper savings. Customer Success is fielding direct calls from the top 3 accounts.

**T+12mo:** The CFO has asked for a re-baselining. Operational cost is 12% lower than baseline, not 40%. CSAT has dipped 6 points in the enterprise segment. Two of the top 10 accounts have asked for contract language requiring human-agent access. The team is quietly designing a "hybrid" rollout for FY+2 that walks back the AI-first framing.

**Failure modes:**

| Name | Severity (T/U/B/O/F/S) | Likelihood | Tripwire | What would change my mind | Citation |
|---|---|---|---|---|---|
| Deflection metric inflation | 2/1/3/1/2/2 | High | Internal "deflection" definition expands within first 3 months | Pre-launch definition lock with audit | Klarna case + plan's lack of metric definition |
| 90% target unsupported by evidence | 1/0/2/0/2/3 | High | Pilot deflection <60% in any segment by month 3 | Two pilot segments hitting ≥70% sustained | Plan cites "industry leaders" without source |
| No accountability framework for AI errors | 3/3/3/2/1/2 | Medium | First customer-impacting AI error reaches social media | Documented liability and escalation policy at launch | Air Canada case |
| Rollout pace too aggressive | 2/2/1/2/1/2 | High | Phase 2 pilot slips past month 4 | Phased rollout dependent on pilot metric gates | McDonald's case |
| Vendor-roadmap dependency | 1/1/2/3/3/1 | Medium | CRM vendor announces roadmap change affecting AI module within 12 months | Contractual commitment to current module capabilities | None — internal signal |

---

## Sample synthesis output (Phase 4)

### Top 5 Confirmed risks (after deduplication across all 7 personas)

| # | Risk | Severity (T/U/B/O/F/S) | Likelihood | Urgency | Tripwire | What would change my mind | Mitigation | Owner shape |
|---|---|---|---|---|---|---|---|---|
| 1 | No accountability framework for AI errors (Air Canada precedent) | 3/3/3/2/1/2 | Medium | **Block** | First customer-impacting AI error reaches a public channel | Documented liability and escalation policy approved by legal before launch | Compliance/Legal (Exec Sponsor) |
| 2 | 90% deflection target unsupported; risk of metric inflation | 2/1/3/1/2/3 | High | **Block** | Pilot deflection <60% in either segment by month 3 | Pre-launch definition of "deflection" locked; two pilot segments at ≥70% sustained for 4 weeks | Product Manager |
| 3 | Top-account renewal exposure from forced AI tier | 3/2/2/1/3/2 | Medium | **Block** | Any of the top 10 accounts asks for contract language requiring human-agent access | Top-account briefings completed before Phase 2; opt-out terms documented in renewals | Customer Success Lead |
| 4 | Rollout pace compresses pilot learning (McDonald's precedent) | 2/2/1/2/1/2 | High | **Patch-fast** | Phase 2 pilot slips past month 4 | Phased rollout with quality gates; ability to pause between Phase 2 and Phase 3 | Product Manager |
| 5 | Vendor-roadmap dependency on AI module | 1/1/2/3/3/1 | Medium | **Monitor** | CRM vendor announces roadmap change affecting AI module | Contractual commitment from vendor for current module capabilities through end of year +1 | Vendor Owner |

### Inflated risks

| # | Risk | Why downgraded |
|---|---|---|
| 1 | Employee morale impact from feared layoffs | Personas raised but no headcount reduction is announced in the plan; absent that, this is anxiety not evidence. Re-examine if a layoff is later announced. |

### Buried risks

| # | Risk | Why nobody names it | How to surface |
|---|---|---|---|
| 1 | "Why now" rationale ("keep pace with industry leaders") is the actual driver, not the savings math | The plan presents savings as the goal but the rationale section betrays competitive anxiety. Naming this would force a conversation about whether the org is reacting to competitor announcements rather than its own data. | Ask in the next review: "If competitors hadn't announced AI rollouts, would we still be doing this with this scope and timeline?" |

### Confidence math

- **Baseline:** 60% (ambitious timeline, no prior org rollouts of similar scope)
- **Top-5 raw risk scores:** 0.22, 0.20, 0.18, 0.16, 0.12 (capped where needed)
- **Unmitigated:** 60% × ∏(1 − 0.22, 0.20, 0.18, 0.16, 0.12) ≈ **20%** → rounded to **20%**
- **Top-3 mitigations applied at 0.7 effectiveness each:**
  - Risk 1 mitigated: 0.22 × 0.3 = 0.066
  - Risk 2 mitigated: 0.20 × 0.3 = 0.060
  - Risk 3 mitigated: 0.18 × 0.3 = 0.054
- **Mitigated:** 60% × ∏(1 − 0.066, 0.060, 0.054, 0.16, 0.12) ≈ **44%** → rounded to **45%**

Sanity: 45 − 20 = 25 (within expected 5–30 range). ✓

---

## Sample exec one-pager (≤300 words — this one is exactly 234)

```markdown
---
plan_title: "AI-First Customer Service Rollout"
generated_at: "2026-05-14"
unmitigated_confidence: 20
mitigated_confidence: 45
report_file: "./time-travel-reports/2026-05-14-1130-ai-cs-rollout-report.md"
ai_source: true
---

# AI-First Customer Service Rollout — Premortem for Decision-Makers

_This plan appears to be AI-authored._

**Source:** `ai-cs-rollout.md` · **Confidence:** unmitigated **20%** → with top-3 mitigations **45%**

## What this plan promises
- Deploy AI customer-service agent to all inquiries within 6 months.
- 90% case deflection rate (resolved without human escalation).
- 40% reduction in customer-service operating cost; CSAT unchanged.

## What could fail (top 3)
1. **AI-error accountability gap** — *Tripwire:* first customer-impacting AI error reaches a public channel. *Mitigation cost:* M.
2. **90% deflection unsupported by evidence** — *Tripwire:* pilot deflection <60% in any segment by month 3. *Mitigation cost:* S.
3. **Top-account renewal exposure** — *Tripwire:* any top-10 account asks for contract language requiring human access. *Mitigation cost:* M.

## 3 questions to ask before approving
1. What's our published policy on financial liability when the AI gives a wrong answer? (Air Canada was held liable for theirs.)
2. Which two customer segments are in the Phase-2 pilot, and what deflection rate would trigger a pause before Phase 3?
3. If competitors hadn't announced AI rollouts, would we still be doing this with this scope and timeline?

---

Full premortem: [`2026-05-14-1130-ai-cs-rollout-report.md`](./time-travel-reports/2026-05-14-1130-ai-cs-rollout-report.md)
```

The third question targets the Buried risk. The exec is the right person to ask it.

---

## What "good" looks like in this run

- AI-Optimism persona fired the loudest, but its findings were grounded in real analogues (Klarna, Air Canada, McDonald's) — not free-floating AI-skepticism.
- The Buried risk surfaced something the original plan was conspicuously avoiding (the "why now" being competitive anxiety, not savings math).
- The top 3 risks each have an observable tripwire that someone could literally watch for in the field.
- The exec one-pager's third question is the most useful 25 words in the artifact — it forces the proposer to defend the timing and scope, not just the implementation.
- Confidence math goes from 20% to 45% — mitigations help substantially but don't manufacture confidence that isn't earned.
