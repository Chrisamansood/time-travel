# Process log template

The audit trail that runs alongside the report. Generated as `<YYYY-MM-DD-HHMM>-<slug>-process.md`. Skipped when `--no-process-log` is set.

## Why this exists

The report is the *deliverable*. The process log is the *receipt*. It exists so that:

- A skeptical reader can audit how findings were produced
- The synthesizer's judgment calls are visible (and contestable)
- Future runs against similar plans can compare deltas
- Disagreements between personas — the most valuable signal — aren't lost in the report's clean prose

If the report is challenged ("how did you get to this Buried risk?"), the process log has the answer.

---

## Skeleton

````markdown
---
plan_title: "{plan_title}"
generated_at: "{YYYY-MM-DD HH:MM}"
report_file: "{path_to_corresponding_report}"
process_log_id: "{YYYY-MM-DD-HHMM-slug}-process"
flags_used: [{flag_list}]
horizons: ["{h1}", "{h2}", "{h3}"]
---

# Process log: {plan_title}

## Plan ingestion (Phase 0)

- **Source resolution:** {how_the_plan_was_obtained — auto-detect_path, explicit_path, pasted_text}
- **Parsing summary:**
  - Goal: {extracted}
  - Domain: {extracted}
  - Stakeholders named: {list}
  - Timeline: {extracted}
  - Success criteria: {extracted_or_'unstated'}
  - Key bets: {extracted}
- **Clarifying questions asked (if any):** {list_with_answers}
- **AI-pattern heuristics fired:** {list_of_patterns_that_matched, or 'none'}
- **AI-Optimism persona included:** {true|false}; **basis:** {`--ai-source` flag | N patterns fired | not included}

---

## User-POV pass (Phase 1)

{The raw user-POV findings before they were condensed for the report.}

---

## Roster selection (Phase 2)

### Picked
| Persona | Source (library / invented) | Rationale |
|---|---|---|
| {name} | library | {why_this_plan_needs_this_POV} |
| {name} | invented | {schema_for_the_new_persona_+_rationale} |

### Considered but dropped
| Persona | Why dropped |
|---|---|
| {name} | {reason — e.g., 'redundant with X', 'low signal for this domain', 'roster cap reached'} |

### Inventions (if any)
{Full_schema_for_each_invented_persona — name, POV, cares_about, overlooks, first_line}

---

## Evidence gathering (Phase 2)

### Web searches run
1. `{query_1}` — {N_results_reviewed}
2. `{query_2}` — {N_results_reviewed}
{...}

### Sources retained for the evidence pack
- [{title}]({url}) — {one_line_justification}
{3_to_5}

### Sources rejected
| Source | Rejected because |
|---|---|
| {title_or_url} | {reason — e.g., 'press-release rewrite', 'vendor-authored', 'pre-2020', 'irrelevant on read'} |

### Adjacent-domain fallbacks (if applicable)
{If_no_direct_analogues_were_found_and_the_skill_fell_back_to_adjacent-domain_cases: list_them_and_note_the_adjacency.}

---

## Per-persona raw outputs (Phase 3)

### {Persona name}

**Narratives:**
- **{h1}:** {verbatim_from_persona_subagent}
- **{h2}:** {verbatim}
- **{h3}:** {verbatim}

**Failure modes flagged:**
| Name | Severity (T/U/B/O/F/S) | Likelihood | Tripwire | What would change my mind | Citation |
|---|---|---|---|---|---|
| {name} | 3/2/1/2/1/2 | High | {observable} | {evidence} | {citation} |

{Repeat for each persona.}

---

## Rebuttal-round disagreements (Phase 3.5)

For each significant disagreement that surfaced:

### {Disagreement_topic_or_finding}
- **{Persona_A}:** {position}
- **{Persona_B}:** {position}
- **Synthesis judgment:** {how_it_was_resolved_in_Phase_4_and_why}

If no disagreements surfaced: write `No substantive disagreements in the rebuttal round. This is a yellow flag — re-examine the roster for diversity. Note: {reasoning_for_why_this_might_be_legitimate, if any}.`

### Cascades identified
- **{Cascade_chain}:** {described}. Personas that flagged it: {list}. Severity uplift: {Low|Medium|High}

---

## Classification calls (Phase 4)

For each non-obvious classification, record the call.

- **Why {risk_name} = Confirmed not Inflated:** {evidence_basis_and_persona_agreement}
- **Why {risk_name} = Inflated not Confirmed:** {what_downgraded_it}
- **Why {risk_name} = Buried not Confirmed:** {the_political_or_hedge_signal_that_marked_it_Buried}

---

## Urgency-tier assignments (Phase 4)

- **{Risk_name} — Block** because {gating_logic}.
- **{Risk_name} — Patch-fast** because {compounding_logic_or_workaround_at_launch}.
- **{Risk_name} — Monitor** because {watch_signal_and_cost_of_premature_mitigation}.

---

## Revised confidence math (Phase 4)

- **Baseline:** {value} — {rationale_for_starting_point}
- **Top-5 risk scores (raw):**
  | Risk | Severity sum | Likelihood weight | Raw score | Capped score |
  |---|---|---|---|---|
  | {name} | {0-18} | {0.3/0.6/1.0} | {} | min({}, 0.25) |
- **Unmitigated confidence:** baseline × ∏(1 − raw_scores) = **{X}%** (rounded to nearest 5)
- **Top-3 mitigation effectiveness applied:**
  | Risk | Mitigation effectiveness | Mitigated score |
  |---|---|---|
  | {name} | 0.7 | {} |
- **Mitigated confidence:** baseline × ∏(top-3 mitigated, rest raw) = **{Y}%** (rounded to nearest 5)
- **Sanity check:** Y − X = {value}. Expected range: 5–30.

---

## Anti-pattern checklist (final pass)

Before finalizing the report, the synthesizer verified each anti-pattern from `anti-patterns.md`:

- [ ] No generic, plan-agnostic risks survived to the Confirmed table
- [ ] Severity scores reflect more than technical impact
- [ ] At least one Buried risk surfaced (or explicit re-examination logged above)
- [ ] Every Confirmed risk has an observable tripwire
- [ ] Every Confirmed risk has a "what would change my mind"
- [ ] Rebuttal round produced substantive disagreement
- [ ] Confirmed count ≤ 7 in the top table
- [ ] Revised plan is an injection, not a rewrite

If any unchecked, note the deviation and why it was accepted.
````

---

## Length expectations

Process logs are denser than reports and don't aim for narrative flow. **1500–3000 words** is typical. The audit value is in completeness, not concision — every judgment call should be traceable.
