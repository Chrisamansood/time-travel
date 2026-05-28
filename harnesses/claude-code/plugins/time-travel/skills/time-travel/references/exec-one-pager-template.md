# Exec one-pager template

A third artifact emitted only when `--for-exec` is set. Generated as `<YYYY-MM-DD-HHMM>-<slug>-exec.md`.

## Purpose

A decision-maker's reading time is the scarcest resource in the org. This artifact is designed to be:

- **Forwarded** — pasted into an email or DM without editing
- **Scanned in 60 seconds** — by someone who hasn't read the original plan
- **Actionable** — produces 3 specific questions the exec can ask, not just risks the exec can worry about

## Hard rules

1. **Word count ≤ 300 words total** (including frontmatter, headings, and bullets). This is non-negotiable. Count mechanically before writing the file.
2. **No appendices, no tables, no nested bullets.** Flat structure only.
3. **No persona names.** The exec doesn't need to know which persona surfaced what.
4. **No methodology talk.** "Cross-pollination", "rebuttal round", "severity lenses" — none of these terms appear in this artifact.
5. **The 3 questions are the most important content.** They're what the exec walks away with.
6. **Link to the full report** at the bottom for anyone who wants depth.

---

## Skeleton

````markdown
---
plan_title: "{plan_title}"
generated_at: "{YYYY-MM-DD}"
unmitigated_confidence: {X}
mitigated_confidence: {Y}
report_file: "{path_to_full_report}"
ai_source: {true|false}
---

# {plan_title} — Premortem for Decision-Makers

**Source:** `{plan_source_filename}` · **Confidence:** unmitigated **{X}%** → with top-3 mitigations **{Y}%**

## What this plan promises

- {promise_in_one_line}
- {promise_in_one_line}
- {promise_in_one_line}

## What could fail (top 3)

1. **{Risk_name_short_noun_phrase}** — *Tripwire:* {observable_signal_one_line}. *Mitigation cost:* S / M / L.
2. **{Risk_name}** — *Tripwire:* {observable_signal}. *Mitigation cost:* S / M / L.
3. **{Risk_name}** — *Tripwire:* {observable_signal}. *Mitigation cost:* S / M / L.

## 3 questions to ask before approving

1. {Question_targeting_top_risk_1 — specific, falsifiable}
2. {Question_targeting_top_risk_2 — specific, falsifiable}
3. {Question_targeting_the_Buried_risk_or_a_cascading_concern}

---

Full premortem: [`{report_filename}`]({relative_path_to_report})
````

---

## How to write each section

### "What this plan promises"

Three lines, each a verbatim or near-verbatim claim the plan makes. Quote the plan's own words where possible — don't paraphrase into vaguer wording. If the plan promises specific numbers, include them.

✗ Bad: "Plan promises significant cost savings."
✓ Good: "Cut customer-service operating cost by 40% within 12 months."

### "What could fail (top 3)"

Pick from the report's Confirmed-Block risks (or top-ranked Patch-fast if no Block risks exist). The criteria:

- Each risk is one short noun phrase (e.g., "Vendor SLA gap", "Compliance deadline slip", "Support team overrun")
- The tripwire is one observable thing the exec or their team would actually see
- Mitigation cost is **S** (no extra budget, this week), **M** (visible budget item, this quarter), or **L** (material budget impact, next planning cycle)

If the exec sees three **L** mitigation costs, that itself is the message — flag it inline:
> *"All three mitigations are material spend; this plan needs a revised business case."*

### "3 questions to ask before approving"

This is the most useful 60 words in the artifact. Each question should:

- Be **specific to this plan** (not "What are the risks?")
- Be **falsifiable** — there's a real answer, not opinion
- **Force the proposer to surface evidence** they may not have included

Good question shapes:
- "What's the rollback plan if [tripwire] fires in week 4?"
- "Which named customer / regulator / vendor has confirmed the [assumption]?"
- "What's the budget for [the mitigation that costs material spend]?"
- "What happened the last time we tried [analogue]?"
- "Who's accountable if [Buried risk] turns out to be true?"

One of the three questions should target the **Buried risk** from the report (if any exists). The exec is the right person to ask the unspoken question.

Bad question shapes (avoid):
- "Are we confident this will work?" (unfalsifiable)
- "Have you considered the risks?" (toothless)
- "What about user adoption?" (vague)

---

## Word-count enforcement

Before writing the file, mechanically count words. Headers and frontmatter count. Bullet markers don't count as words.

If over 300:
1. Shorten the promise lines first (they have the most filler)
2. Shorten the tripwires next (keep observability, cut adjectives)
3. Shorten the questions last (the most valuable content)
4. If still over, the report's risks are unclear — the issue isn't word count, it's that the risk names are too long. Re-extract.

If under 200 — the artifact is too thin. Either the report doesn't have enough material (re-run with more personas) or the extraction is timid.

## If ai_source is true

Add a 6-word note immediately after the title line:

> _This plan appears to be AI-authored._

This counts toward the 300-word limit. It's worth the cost — it primes the exec to read with appropriate skepticism without you having to spell out why.
