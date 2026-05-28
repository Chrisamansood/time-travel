---
name: time-travel
description: Run a multi-agent premortem on any plan. Dispatches 5–7 stakeholder personas, synthesizes Confirmed / Inflated / Buried risk classification, and produces HTML + Markdown reports. Use this skill when the user invokes /time-travel:run, or asks to "premortem", "pre-mortem", "stress test", "time travel" a plan, "find failure modes", or "what could go wrong with this".
---

# Time Travel (Codex Skill — thin wrapper)

This skill shells out to the `time-travel` Python CLI. Ensure it is installed first:

```bash
pip install time-travel-premortem
# or: pip install -e /path/to/this/repo
```

## Invocation

When this skill is triggered:

1. Resolve the plan source (see auto-detect order below).
2. Run: `time-travel run <plan_source> --output ./time-travel-reports`
3. Capture stdout. Parse the JSON block after `---REPORT---` to extract `report_path_html`, `report_path_md`, and `tldr`.
4. Surface the TL;DR in chat and print the file paths.

## Auto-detect order (when source is omitted)

1. Latest `.md` file in `./plans/`
2. Latest `.md` file in `~/.claude/plans/`
3. Last substantial assistant message in the current conversation
4. Prompt the user to paste the plan

## Flags (passed through to the CLI)

`--fast`, `--horizons`, `--output`, `--for-exec`, `--ai-source`, `--no-process-log`, `--provider`, `--model`
