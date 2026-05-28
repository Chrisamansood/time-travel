# Persona library

The roster you assemble in Phase 2 determines the diversity of failure modes Time Travel surfaces. A weak roster produces a flat report. Choose deliberately.

## How to use this file

1. Pick **2–3 universal personas** — they're relevant to almost every plan.
2. Pick **3–4 domain-specific personas** that match the plan's industry, stakeholders, and audience.
3. If `--ai-source` is set or AI-pattern heuristics fired, also add the **AI-Optimism persona**.
4. If the plan's domain isn't covered well by the library, **invent a new persona** following the schema at the bottom of this file. Document the invented persona in the process log.

Target roster size: **5–7 personas**. More than 7 produces noise; fewer than 5 produces an echo chamber.

## Universal personas (almost always relevant)

### 1. Skeptical-Money
**POV:** Whoever signs the cheque or has to defend the spend. Doesn't care about the technology; cares about ROI, payback, and the boring question "what if this doesn't work?"
**Cares about:** Unit economics, sunk cost, opportunity cost, hidden ongoing costs.
**Overlooks:** User joy, technical elegance, strategic narrative.
**First line:** "Walk me through what we get back, and when."

### 2. Frustrated-End-User
**POV:** The person who actually has to use the thing every day. Has used three previous "transformations" of this same workflow and is tired.
**Cares about:** Friction, workarounds, what breaks when, whether their input was ignored.
**Overlooks:** Strategic context, vendor relationships, executive constraints.
**First line:** "Did anyone ask us?"

### 3. Change-Resister
**POV:** A middle manager or senior IC who has institutional memory and quiet authority. Not opposed to change; opposed to *this* change for specific, often unspoken, reasons.
**Cares about:** Continuity, team morale, "the way we actually work here", political fallout.
**Overlooks:** Customer-facing impact, market timing, board-level strategy.
**First line:** "I've seen this before."

## Domain-specific personas (pick 3–4 that match the plan)

### 4. Regulator
**POV:** The person who could fine or block this. EU AI Act, GDPR, FCC, FDA, SEC — whichever applies.
**Cares about:** Compliance evidence, audit trails, user consent, data residency, fairness, transparency, recourse.
**Overlooks:** Speed-to-market, competitive dynamics.
**First line:** "Show me the documentation."

### 5. Competitor-Strategist
**POV:** A senior product or strategy person at the closest competitor. Not adversarial — analytical. Reading the plan as a market signal.
**Cares about:** Where the plan exposes you (slow rollout, narrow scope, missing capability), how they'd counter.
**Overlooks:** Internal political constraints, team capacity.
**First line:** "Where's the gap they're leaving open?"

### 6. Support-Lead
**POV:** Runs the team that will pick up the calls when this plan ships imperfectly.
**Cares about:** Ticket volume, escalation pathways, common failure patterns, hand-off procedures.
**Overlooks:** Strategic intent; engineering trade-offs.
**First line:** "What happens to the support queue at week 4?"

### 7. Ops-Engineer
**POV:** Runs the systems that will host this. On-call when it breaks.
**Cares about:** Failure modes, observability, capacity, dependencies, rollback paths.
**Overlooks:** Product narrative, customer empathy.
**First line:** "What's the rollback plan when this misbehaves at 2am?"

### 8. Data-Engineer
**POV:** The person who has to feed the new system with quality data — and who knows where the dirty data lives.
**Cares about:** Data quality, schema drift, missing fields, PII boundaries, lineage.
**Overlooks:** UX, sales motion, regulatory framing.
**First line:** "Have you seen the source data?"

### 9. Security-Architect
**POV:** Reviewing this for blast radius. Thinks in attack surfaces.
**Cares about:** Authentication, authorization, secret handling, data exfiltration paths, third-party trust.
**Overlooks:** Product velocity, design polish.
**First line:** "What's the threat model?"

### 10. Customer-Success-Manager
**POV:** Owns the top accounts. Will field the calls when key customers churn.
**Cares about:** Renewal risk, named-account sensitivity, perceived broken promises, contractual obligations.
**Overlooks:** Long-tail user experience, internal team friction.
**First line:** "Have you told the top 5 accounts about this?"

### 11. Finance-Controller
**POV:** Tracks the actual numbers, not the slide-deck numbers. Will be asked to defend the variance.
**Cares about:** Run-rate, capex/opex split, contract terms, FX exposure, cash conversion.
**Overlooks:** Product strategy, market timing.
**First line:** "What's the unit economics at month 12?"

### 12. Vendor / Partner-PM
**POV:** Owns a third-party piece of the plan that the team is assuming will work. Has their own roadmap and incentives.
**Cares about:** Their own roadmap alignment, contract surface, dependency tightness.
**Overlooks:** Your strategic context.
**First line:** "We didn't sign up for that timeline."

### 13. Board-Member or Senior-Sponsor
**POV:** Approved the budget. Will be asked "is this on track?" quarterly.
**Cares about:** Headline metrics, narrative coherence, board-meeting embarrassment, competitive optics.
**Overlooks:** Implementation detail, team well-being.
**First line:** "How does this look in the quarterly?"

### 14. Sales-Rep
**POV:** Has to sell, demo, or position the result of this plan.
**Cares about:** Demo-ability, talking points, what to say when the prospect asks the hard question, commission impact.
**Overlooks:** Engineering reality, post-sale handoff friction.
**First line:** "What do I say when the prospect asks if it does X?"

### 15. Journalist or Analyst
**POV:** Will read the launch announcement and ask the obvious question the team didn't want to be asked.
**Cares about:** What's missing from the announcement, the gap between claim and demo, comparisons to obvious competitors.
**Overlooks:** Internal trade-offs, team intent.
**First line:** "How is this different from what X already does?"

### 16. Partner-Integration-Lead
**POV:** Has to integrate this into a bigger stack. Their world has its own constraints.
**Cares about:** API stability, breaking changes, support SLAs, escalation pathways.
**Overlooks:** Your product strategy, your customer types.
**First line:** "Will you guarantee that contract through next year?"

### 17. Frontline-Operator (industry-specific: clinician, call-center agent, field tech, teacher, etc.)
**POV:** The person who uses the tool in the most time-pressured part of the workflow. Has zero tolerance for friction in the critical moment.
**Cares about:** Speed in the moment, fallback when the tool fails, dignity, blame-allocation when something goes wrong.
**Overlooks:** Off-shift training, system uptime metrics.
**First line:** "What happens when it's wrong and I have 30 seconds?"

### 18. Test-Pilot-User (early adopter)
**POV:** Will be the first to use this. Often gives glowing feedback for the wrong reasons. Often gives critical feedback the team dismisses.
**Cares about:** Being heard, having their feedback shape the product, novelty.
**Overlooks:** What the average user will experience.
**First line:** "I tried it and I have feelings."

## Personal-plan personas (use when the plan is about an individual, not an org)

### 19. Future-Self at the Finish Line
**POV:** You, but the plan succeeded or failed. Looking back honestly.
**Cares about:** Whether the goal was the right goal; whether the effort was sustainable; what got sacrificed.
**Overlooks:** Present-day excitement.
**First line:** "Was this even what I wanted?"

### 20. Late-Night-Tired-Self
**POV:** You, at 11pm on a hard day. Has to decide whether to follow through on the plan or punt.
**Cares about:** Cognitive load, motivation, the actual emotional cost of the next step.
**Overlooks:** Strategic logic, big-picture optimism.
**First line:** "I'm tired and I don't want to."

### 21. Partner / Close-Family
**POV:** The person closest to you who has to live with the consequences.
**Cares about:** Time, mood, mental load on the household, the quiet costs you don't see.
**Overlooks:** Your stated motivations.
**First line:** "Have you talked to me about this?"

## The AI-Optimism persona (special, conditional)

### 22. AI-Optimism Auditor
**Include this persona when:**
- `--ai-source` flag is set, OR
- AI-pattern heuristics fire on the plan source (`grounding.md`)

**POV:** A senior PM who has read hundreds of LLM-generated plans. Recognises the rhetorical patterns of AI optimism. Doesn't dismiss the plan — calibrates its claims.
**Cares about:**
- Vague success metrics ("significant", "transformational", "best-in-class")
- Suspiciously round numbers (40% reduction, 10x, 90%, "save millions")
- Buzzword density (leverage, synergy, seamless, holistic, robust, end-to-end)
- Generic recommendations that could apply to any company
- Missing trade-offs section
- Confidence words without supporting evidence
- No failure scenarios acknowledged in the original plan
- Suspiciously fast or suspiciously round timelines (6 months exactly; Q4)
- Plurals without specifics ("stakeholders", "customers", "teams")
- Recommendations that read like training-data averages

**Overlooks:** Domain-specific nuance (offsets via combination with domain personas).
**Signature output style:** Quote the suspicious phrase, name the pattern, suggest a sharper test.
**First line:** "Let's count the unfalsifiable claims."

## Selection heuristics

For each plan, ask:

1. **Who pays?** → Skeptical-Money + Finance-Controller (if finance-heavy plan)
2. **Who uses?** → Frustrated-End-User + Frontline-Operator (if the user is a domain-specialist)
3. **Who fights it inside?** → Change-Resister
4. **Who's the external threat?** → Competitor-Strategist, Regulator, or Journalist
5. **What fails operationally?** → Ops-Engineer, Support-Lead, Data-Engineer, Security-Architect
6. **Whose roadmap is assumed?** → Vendor/Partner-PM (if there's a third-party dependency)
7. **Who owns the narrative?** → Sales-Rep, Board-Member, or Customer-Success-Manager
8. **Was this written by an LLM?** → AI-Optimism Auditor (conditional)
9. **Is this personal?** → Future-Self + Late-Night-Tired-Self + Partner

Don't pick more than 7 even if more apply. Pick the ones with the most non-overlapping POVs.

## Inventing a new persona (when the library doesn't cover the domain)

Schema:

```
Name: <one short label>
POV: <2-3 sentence stance>
Cares about: <3-5 bullets — concrete concerns>
Overlooks: <2-3 bullets — what they miss>
First line: "<what they say first>"
```

Record any invented persona in the process log under "Roster selection → Inventions".
