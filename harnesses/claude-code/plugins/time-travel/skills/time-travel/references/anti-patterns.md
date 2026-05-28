# Anti-patterns

Common ways this skill fails — read this before finalizing any report.

The synthesizer should check every anti-pattern below in the final pass (mirrored in the process log's anti-pattern checklist). If you catch yourself doing any of these, fix it before writing the artifacts.

---

## 1. Generic, plan-agnostic risks

**The failure:** Confirmed risks read like a generic risk register: "scope creep", "team burnout", "stakeholder misalignment", "technical debt accumulation".

**Why it happens:** Personas default to risk-management vocabulary instead of looking at *this* plan.

**Fix:** Every Confirmed risk must reference something specific to this plan — a named system, a named timeline, a named dependency, a named customer segment, a named regulation. If you can copy the risk into another plan unchanged, it's too generic.

**Counter-example:**
- ✗ "Scope creep risk"
- ✓ "The plan compresses 4 vendor integrations into Q3; historically Q3 has 2 weeks of holiday capacity loss this team hasn't accounted for"

---

## 2. Technical-only severity

**The failure:** Every risk is scored heavily on financial and ops_load, and zero on trust_damage or user_pain.

**Why it happens:** Engineers and PMs default to measurable, technical impacts. Trust and user pain feel softer, so they get scored low.

**Fix:** For every Confirmed risk, ask: *Who feels this first? Is it the user, the team, or the books?* If you can't articulate user_pain or trust_damage, the risk may be incompletely formulated.

---

## 3. No Buried risks surfaced

**The failure:** The Buried section is empty (or `_None_`).

**Why it happens:** Personas defaulted to safe, technical risks. The user-POV pass was thin. Nobody asked: "what aren't we saying?"

**Fix:** Re-examine:
- The rebuttal-round disagreements — was anyone hedging?
- The user-POV pass — did "what feels untrustworthy" come back empty?
- The plan itself — is there an obvious named dynamic (a vendor, a key person, a previous failed attempt) that the plan is conspicuously not naming?

If after re-examination there truly is no Buried risk, log the re-examination in the process log. *Don't* fabricate one. But the default assumption is that every plan has at least one.

---

## 4. Missing tripwires

**The failure:** A Confirmed risk in the top-risks table has no tripwire, or a vague tripwire ("user complaints increase").

**Why it happens:** Personas wrote tripwires that describe outcomes, not signals.

**Fix:** A tripwire is a **specific, observable, early** signal. Test: could someone set a dashboard alert for it?

**Counter-example:**
- ✗ "User satisfaction drops"
- ✓ "NPS in the EU segment drops below 30 in the first monthly survey post-launch"

---

## 5. Missing "what would change my mind"

**The failure:** A Confirmed risk has no "what would change my mind" entry, or it's tautological ("if the risk doesn't happen").

**Why it happens:** It's the hardest column to write. Easy to skip.

**Fix:** For each risk, ask: *What evidence would let me legitimately downgrade this risk from Confirmed to Inflated?* The answer should be a specific piece of information someone could go fetch.

**Counter-example:**
- ✗ "If the system works."
- ✓ "Pilot data from 3 of the largest 5 accounts showing >70% deflection in their first 30 days."

---

## 6. No disagreement in the rebuttal round

**The failure:** The rebuttal-round section reads "all personas agreed".

**Why it happens:**
- The roster is too homogeneous (all internal-facing personas, or all external-facing)
- The personas were prompted too similarly
- Strong personas (e.g., Skeptical-Money) dominated and the others echoed

**Fix:** Re-pick the roster with deliberate POV diversity. At minimum, one of each: someone who pays, someone who uses, someone who fights it inside, someone outside the org. Re-dispatch Phase 3.5.

If after re-running there's still agreement, the report should note this explicitly — strong agreement across diverse personas is itself a signal (likely a real, easy-to-see risk), but it should be acknowledged, not glossed.

---

## 7. Confirmed count > 7 in the top table

**The failure:** The top-risks table has 9, 12, 15 Confirmed risks.

**Why it happens:** Deduplication wasn't aggressive enough, or the plan is genuinely too broad.

**Fix:**
- Re-dedupe with stricter family grouping.
- If still > 7 after deduplication, the plan is over-scoped. Flag this in the TL;DR: *"This plan has {N} blocking risks. Reconsider scope or decompose before proceeding."*

---

## 8. Revised plan is a wholesale rewrite

**The failure:** The "revised plan" section bears little resemblance to the original — different structure, different sequencing, different voice.

**Why it happens:** The synthesizer drifted into "rewriting the plan correctly" instead of "injecting mitigations into the existing plan".

**Fix:** The revised plan should be readable as a diff against the original. Same phases, same milestones, same voice — just with mitigations folded in as sub-bullets and a Pre-flight checks section at the top for Block risks. If structural change is needed, that's a finding for the report's mitigations section, not a quiet rewrite.

---

## 9. Exec one-pager exceeds 300 words

**The failure:** The `--for-exec` artifact is 450 words.

**Why it happens:** Trying to capture nuance the artifact isn't designed for.

**Fix:** Mechanically count. Cut promise-lines first, tripwires second, questions last. If still over, the underlying risks are over-named — re-extract shorter risk names from the report.

---

## 10. Suspiciously crisp confidence numbers

**The failure:** Unmitigated 73%, mitigated 88%.

**Why it happens:** The math (heuristic by design) is being reported with false precision.

**Fix:** Round both numbers to nearest 5 before writing. 73 → 75. 88 → 90. The confidence math is honest about its imprecision.

---

## 11. Citation-free severity scores

**The failure:** Severity columns are filled in but no persona output supports the scores.

**Why it happens:** The synthesizer is filling in scores by gut, not by aggregating persona inputs.

**Fix:** Every score in the report should trace back to at least one persona output in the process log. If a score has no support, drop the lens to 0 or re-examine the persona outputs.

---

## 12. Speaking for personas the synthesizer invented

**The failure:** An invented persona's output is more polished than the library-defined personas' outputs — and conveniently aligned with the synthesizer's prior view.

**Why it happens:** Inventing personas is permitted but it's where bias sneaks in. The synthesizer accidentally creates a persona that says what they wanted to surface.

**Fix:** When inventing a persona, write the schema first (POV, cares about, overlooks, first line) and stick to it. If the invented persona's output reads suspiciously aligned with the synthesizer's earlier guesses, treat its findings with extra skepticism.

---

## 13. AI-Optimism persona over-included or under-included

**The failure:** The persona is added for every plan (over-inclusion) or never added even when patterns clearly fire (under-inclusion).

**Fix:** Strict heuristic in `grounding.md`. Include only when:
- `--ai-source` is set, OR
- 3+ AI-pattern heuristics fire

If 1–2 patterns fire, note in the process log but don't add the persona — the threshold matters.

---

## 14. Process log skipped without flag

**The failure:** No process log artifact, but `--no-process-log` wasn't set.

**Why it happens:** The synthesizer thought "the report covers it".

**Fix:** Default is always two artifacts (report + process log). Only skip when the user explicitly sets `--no-process-log`.

---

## 15. Personas given the original plan's risks section

**The failure:** The persona prompt included the plan's own "risks" section, and personas anchored on it.

**Why it happens:** When passing the full plan to personas in Phase 3, the original "risks" section pre-loads them with the team's existing framing.

**Fix:** It's fine to include the original risks section in the plan passed to personas, but the per-persona prompt explicitly instructs them to look beyond it. If multiple personas' outputs read like elaborations of the original risks section, the personas weren't independent enough — re-prompt with stronger anti-anchoring language.

---

## Final-pass checklist

Mirrored in `process-log-template.md`. Verify each before writing artifacts:

- [ ] No generic, plan-agnostic risks in the Confirmed table
- [ ] Severity scores reflect more than financial/ops dimensions
- [ ] At least one Buried risk surfaced, OR re-examination logged
- [ ] Every Confirmed risk has an observable tripwire
- [ ] Every Confirmed risk has a "what would change my mind"
- [ ] Rebuttal round produced substantive disagreement
- [ ] Confirmed count ≤ 7 in the top table
- [ ] Revised plan is an injection, not a rewrite
- [ ] If `--for-exec`: exec artifact ≤ 300 words (mechanical count)
- [ ] Confidence numbers rounded to nearest 5
- [ ] Every score in the report traces to a persona output in the process log
- [ ] Process log written unless `--no-process-log` is set
