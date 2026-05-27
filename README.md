# Time Travel

> A multi-agent premortem skill for Claude Code. Sends stakeholder personas to the future, brings back a structured risk classification, and rewrites your plan with mitigations folded in.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue.svg)](https://code.claude.com/docs/en/plugins)

---

## Why this exists

LLMs produce plans confidently. Executives, increasingly, take those plans at face value.

Time Travel is the rebuttal. Point it at any plan — yours, your team's, or one your AI assistant just wrote — and it dispatches 5–7 stakeholder personas to the future. Each one stands at month 3, month 6, and month 12, looks back at how the plan unfolded, and tells you what broke.

You get:
- A **risk classification** that separates real, evidence-backed concerns (Confirmed) from manufactured drama (Inflated) from politically unspoken truths (Buried).
- A **tripwire** for each top risk — the first signal you'd see in the field.
- A **"what would change my mind"** clause for each risk — the specific evidence that would let a decision-maker safely proceed.
- A **revised plan** with mitigations folded in inline.
- An optional **300-word exec one-pager** designed to be forwarded.

## What makes this different from other premortem skills

Several premortem skills already exist for Claude Code. We borrow generously from the best ideas in each (see [Credits & influences](#credits--influences)). Time Travel adds:

| Capability | Why it matters |
|---|---|
| **Multi-horizon timeline narratives** (T+3 / T+6 / T+12 months per persona) | Most premortems use one timeframe. Real plans fail differently at different time scales — early-signal failures, mid-game drift, mature outcomes. |
| **Web-search grounding** | Personas come back with citations to real-world analogue failures (Klarna's AI rollback, Air Canada's chatbot liability, etc.) — not just hypotheticals. |
| **Parallel persona subagents with isolated context** | Each persona reasons in its own context window, so the regulator doesn't echo the CFO. The rebuttal round then catches blind spots and cascading failures. |
| **AI-Optimism persona** (auto-included when AI patterns detected) | Specifically tuned to spot the rhetorical fingerprints of LLM-generated plans: vague success criteria, suspiciously round numbers, missing trade-offs, training-data averages. |
| **Revised plan output, not just a risk registry** | The plan is rewritten with mitigations folded in inline — preserving structure and voice, marking injections clearly. |
| **Exec one-pager mode** (`--for-exec`) | A strict 300-word artifact built to be forwarded to a decision-maker. Three risks, three tripwires, three questions to ask before approving. |
| **"What would change my mind" column** | Operationalizes skepticism. For each risk, the evidence that would justify downgrading it. |

## Install

```sh
/plugin marketplace add chrisaman/time-travel
/plugin install time-travel@time-travel
/reload-plugins
```

Once installed, the skill is invoked as `/time-travel:run`.

## Usage

### Basic

```sh
/time-travel:run path/to/your-plan.md
```

Auto-detect mode (no argument):
```sh
/time-travel:run
```

Auto-detect looks for the most recent plan in `./plans/`, then `~/.claude/plans/`, then falls back to the last substantial assistant message in the conversation, then prompts you.

### With flags

```sh
# Treat the plan as AI-authored — adds the AI-Optimism persona
/time-travel:run path/to/plan.md --ai-source

# Also generate a 300-word exec one-pager
/time-travel:run path/to/plan.md --ai-source --for-exec

# Cheap single-call mode (skips parallel subagent dispatch)
/time-travel:run path/to/plan.md --fast

# Custom time horizons
/time-travel:run path/to/plan.md --horizons 1mo,6mo,2y

# Custom output directory
/time-travel:run path/to/plan.md --output ./reviews/

# Skip the process log (just emit the report)
/time-travel:run path/to/plan.md --no-process-log
```

### Output

By default, Time Travel writes two files to `./time-travel-reports/`:

- `<YYYY-MM-DD-HHMM>-<slug>-report.md` — the full report (2500–4000 words)
- `<YYYY-MM-DD-HHMM>-<slug>-process.md` — the audit trail (1500–3000 words)

With `--for-exec`, a third file:

- `<YYYY-MM-DD-HHMM>-<slug>-exec.md` — the 300-word exec one-pager

Override the output directory via the `--output` flag or the `TIME_TRAVEL_REPORTS_DIR` environment variable.

## What the output looks like

See [`plugins/time-travel/skills/time-travel/references/example-run.md`](plugins/time-travel/skills/time-travel/references/example-run.md) for a full worked walkthrough on a synthetic plan, including:

- Which AI-patterns fire on a typical AI-generated rollout plan
- How the roster is selected
- A sample persona output across T+3/6/12 months
- The synthesized top-5 Confirmed risks with tripwires and mitigations
- The Buried risk that the team was conspicuously avoiding
- The confidence math (unmitigated 20% → mitigated 45%)
- The 234-word exec one-pager

## How it works under the hood

Six phases:

0. **Ingest** the plan, parse goal/domain/stakeholders, detect AI-pattern signals.
1. **User-POV pass** — capture what the intended users wanted, before going adversarial.
2. **Roster + evidence** — pick 5–7 personas adaptively from the [library](plugins/time-travel/skills/time-travel/references/persona-library.md); fetch 3–5 real-world analogue failure cases via web search.
3. **Parallel persona fan-out** — each persona runs in its own subagent and produces timeline narratives + failure modes with severity scores, tripwires, and "what would change my mind" entries.
4. **Rebuttal round** — each persona sees a digest of the others' findings and rebuts/extends. Catches blind spots and cascading failures.
5. **Synthesis** — deduplicate, classify into Confirmed / Inflated / Buried, assign urgency tiers (Block / Patch-fast / Monitor), compute revised confidence.
6. **Artifacts** — write the report, process log, and (optionally) exec one-pager.

The full design lives in [`plugins/time-travel/skills/time-travel/SKILL.md`](plugins/time-travel/skills/time-travel/SKILL.md) and the eleven reference docs alongside it.

## Use cases

- **Before approving a Claude-generated plan**, especially one heading to leadership.
- **At the kickoff of any multi-quarter initiative** — the wider the horizon, the more value the multi-month narratives surface.
- **Stress-testing a strategic announcement** before it goes external.
- **Personal plans** with horizons of months or longer (use the personal-plan personas).
- **As a discipline tool** — even a quick `--fast` run forces the question "what's the tripwire for failure?"

## Use cases this skill is *not* well-suited to

- Code-level decisions (use a code review skill).
- Tactical day-of decisions where the horizon is hours or days.
- Plans where you don't actually want disagreement — Time Travel will surface it.

## Credits & influences

Time Travel learns from existing premortem skills and the people who built them. It borrows ideas (with our own labels and our own additions); the original creators deserve credit:

- **[carlkibler/agent-skills](https://github.com/carlkibler/agent-skills)** — multi-agent persona dispatch, the second-pass rebuttal pattern, severity dimensions beyond technical impact, the two-artifact (report + process log) pattern, anti-patterns guidance for premortem skills.
- **[borghei/Claude-Skills](https://github.com/borghei/Claude-Skills)** — the structure of risk classification (real-evidence-backed vs unlikely-but-loud vs politically-unspoken), urgency tiering for blocking risks, evidence-requirement enforcement.
- **[neurofoo/agent-skills](https://github.com/neurofoo/agent-skills)** — per-risk early-warning signals (tripwires), the revised-confidence pattern.
- **Gary Klein** — *"Performing a Project Pre-Mortem"*, *Harvard Business Review* (2007). The original technique.
- **Daniel Kahneman**, *Thinking, Fast and Slow* — prospective hindsight.
- **Amy Edmondson**, *The Fearless Organization* — psychological safety as a precondition for surfacing Buried risks.

All terminology in Time Travel is original to this skill. Where ideas were borrowed, vocabulary was renamed (e.g., the Confirmed / Inflated / Buried taxonomy, the Block / Patch-fast / Monitor urgency tiers, the Rebuttal Round, the User-POV Pass). The intent is to acknowledge debts honestly while not re-using prior skills' labels.

## Contributing

Issues and pull requests welcome. Particular asks:

- **More personas** in the library, especially for domains beyond the ones covered (legal, healthcare, education, government, manufacturing).
- **Refinements to the AI-pattern heuristics** in `grounding.md` — these will evolve as LLM writing styles shift.
- **More worked examples** in `example-run.md` for different industries.
- **Calibration data** — if you run Time Travel and the predicted failure modes don't (or do) match what actually happened months later, that's gold for tuning.

Before opening a PR, please run `/time-travel:run` against a synthetic plan and confirm the output structure is intact.

## License

MIT. See [LICENSE](LICENSE).

## Author

Built by Chris Sood while figuring out how to keep AI-generated plans honest in enterprise settings. Feedback and counter-examples both welcome.
