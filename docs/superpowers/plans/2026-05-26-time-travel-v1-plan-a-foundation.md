# Time-Travel v1.0 — Plan A: Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize the repo as a git project, restructure files into the polyglot monorepo layout, define the canonical `Report` data model with JSON round-trip, the `LLMProvider` ABC, and a fully-parsed CLI skeleton so that `pip install -e .` and `time-travel --help` work.

**Architecture:** Python package at `src/time_travel/`. Data model in `models.py` using `dataclasses_json` for JSON serialization. CLI in `cli.py` using `argparse`; all subcommands are stubbed (raise `NotImplementedError` or print "not yet implemented"). `providers/base.py` defines the abstract interface all provider adapters will implement in Plan B. No LLM calls, no file I/O beyond what the CLI parses.

**Tech Stack:** Python ≥3.10, `dataclasses_json>=0.6`, `pytest>=8`, `ruff>=0.4`, `mypy>=1.10`. No LLM SDK dependencies needed for Plan A (they appear in `pyproject.toml` but are not imported by the modules built here).

**⚠️ Repo path note:** The working directory has a space in the path. Always quote it:
`"/Users/macbook/Documents/Chris developed Applications /time-travel"`

**Plan sequence:** This is Plan A of 4. Plans B (engine), C (renderers), D (harnesses+CI) follow.

---

## File map

| File | Action | Responsibility |
|---|---|---|
| `.gitignore` | Create | Standard Python ignores |
| `pyproject.toml` | Create | PEP 621 package config, entry point, dev deps |
| `src/time_travel/__init__.py` | Create | Empty — marks package root |
| `src/time_travel/models.py` | Create | `Report` + all sub-dataclasses, JSON round-trip |
| `src/time_travel/providers/__init__.py` | Create | Empty |
| `src/time_travel/providers/base.py` | Create | `LLMProvider` ABC |
| `src/time_travel/render/__init__.py` | Create | Empty |
| `src/time_travel/search/__init__.py` | Create | Empty |
| `src/time_travel/personas/__init__.py` | Create | Empty |
| `src/time_travel/cli.py` | Create | Argument parser + stub dispatch |
| `tests/__init__.py` | Create | Empty |
| `tests/test_models.py` | Create | Report construction + JSON round-trip tests |
| `tests/test_provider_base.py` | Create | LLMProvider ABC contract tests |
| `tests/test_cli.py` | Create | Argument parsing tests |
| `harnesses/claude-code/plugins/time-travel/` | Create (migrate) | Move existing plugin files here |
| `harnesses/codex/skills/time-travel/` | Create (stub) | Empty SKILL.md stub |
| `harnesses/gemini/` | Create (stub) | Empty directory |
| `examples/sample-plan.md` | Create | Fixture used by tests and smoke tests in later plans |
| `CHANGELOG.md` | Modify | Add v1.0.0-dev entry |

---

### Task 1: Verify remote state + initialize git

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Check whether the remote GitHub repo has content**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
curl -s https://api.github.com/repos/chrisaman/time-travel | python3 -c "import sys,json; d=json.load(sys.stdin); print('default_branch:', d.get('default_branch','N/A'), '| size:', d.get('size','N/A'), 'KB', '| private:', d.get('private'))"
```

Expected (if repo exists and is accessible):
```
default_branch: main | size: <N> KB | private: False
```

If `"message": "Not Found"` is returned, the remote repo doesn't exist yet — you will need to create it on GitHub (`gh repo create chrisaman/time-travel --public`) before Step 4.

- [ ] **Step 2: Initialize git**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git init
```

Expected: `Initialized empty Git repository in ...`

- [ ] **Step 3: Create `.gitignore`**

Create the file at `/Users/macbook/Documents/Chris developed Applications /time-travel/.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
*.egg
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.so
*.pyd

# Reports (user-generated output — not committed)
time-travel-reports/

# macOS
.DS_Store

# IDE
.idea/
.vscode/
*.swp
```

- [ ] **Step 4: Connect to remote and make first commit of existing files**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git remote add origin https://github.com/chrisaman/time-travel.git
git add .gitignore README.md LICENSE CHANGELOG.md
git commit -m "chore: init repo with existing MIT-licensed files"
```

If the remote has content (from Step 1), first pull before committing:
```bash
git fetch origin
git rebase origin/main   # or: git reset --hard origin/main
# then re-add and commit as above
```

Expected: commit created, no errors.

---

### Task 2: Restructure existing files into polyglot monorepo layout

**Files:**
- Create: `harnesses/claude-code/plugins/time-travel/` (directory, migrated from `plugins/time-travel/`)
- Create: `harnesses/codex/skills/time-travel/SKILL.md` (stub)
- Create: `harnesses/gemini/` (empty dir)
- Create: `examples/sample-plan.md`

- [ ] **Step 1: Create harness directory structure**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
mkdir -p harnesses/claude-code/plugins/time-travel
mkdir -p harnesses/codex/skills/time-travel
mkdir -p harnesses/gemini
mkdir -p src/time_travel/providers
mkdir -p src/time_travel/render
mkdir -p src/time_travel/search
mkdir -p src/time_travel/personas
mkdir -p src/time_travel/templates
mkdir -p tests
mkdir -p examples
mkdir -p scripts
```

- [ ] **Step 2: Move existing plugin content to harnesses/**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
cp -r plugins/time-travel/. harnesses/claude-code/plugins/time-travel/
```

Verify the copy worked:
```bash
ls harnesses/claude-code/plugins/time-travel/
```

Expected output includes: `.claude-plugin/`  `skills/`

- [ ] **Step 3: Create Codex skill stub**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/harnesses/codex/skills/time-travel/SKILL.md`:

```markdown
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
```

- [ ] **Step 4: Create a Gemini harness placeholder**

```bash
touch "/Users/macbook/Documents/Chris developed Applications /time-travel/harnesses/gemini/.gitkeep"
```

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/harnesses/gemini/README.md`:

```markdown
# Gemini CLI Harness

Planned for v1.1. See the main README for the current harness support matrix.
```

- [ ] **Step 5: Create the sample plan fixture**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/examples/sample-plan.md`:

```markdown
# Plan: Launch a SaaS MVP in 90 Days

## Goal
Ship a working SaaS product with paying customers by end of Q3.

## Timeline
- Week 1–2: Finalize requirements and design
- Week 3–8: Core feature development (auth, billing, main feature)
- Week 9–10: QA and bug fixes
- Week 11: Beta with 10 design-partner customers
- Week 12: Public launch

## Success criteria
- 10 paying customers on day 1 of launch
- NPS ≥ 30 from beta users
- <2% error rate on core feature

## Key bets
- We can build billing with Stripe in under a week
- Customers will tolerate rough UX in beta
- One engineer can carry the backend solo

## Stakeholders
- Founding engineer (builder)
- Early-access customers (10 signed up)
- Investor (watching the 90-day clock)
```

- [ ] **Step 6: Remove the now-redundant top-level `plugins/` directory** (only after verifying harnesses/ copy in Step 2)

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
# Verify harnesses copy is intact first
ls harnesses/claude-code/plugins/time-travel/skills/time-travel/SKILL.md
# Only remove if the above ls succeeds
rm -rf plugins/
```

Also remove the duplicate repo at `Developed Skills /time-travel` by noting it to the user — don't automate deletion of a sibling directory.

- [ ] **Step 7: Commit restructure**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git add harnesses/ examples/ scripts/ src/ tests/ harnesses/
git rm -r plugins/ 2>/dev/null || true
git add -A
git commit -m "chore: restructure into polyglot monorepo layout

- Move plugins/time-travel → harnesses/claude-code/plugins/time-travel
- Add harnesses/codex and harnesses/gemini stubs
- Scaffold src/time_travel/, tests/, examples/, scripts/
- Add sample-plan.md fixture"
```

---

### Task 3: pyproject.toml + dev environment

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create `pyproject.toml`**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "time-travel-premortem"
version = "1.0.0.dev0"
description = "Multi-agent premortem for plans. Provider-agnostic, HTML + Markdown reports."
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "Chris Sood", email = "chrisaman.sood@gmail.com"}]
requires-python = ">=3.10"
keywords = ["premortem", "ai", "risk-analysis", "planning"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
dependencies = [
    "anthropic>=0.30",
    "openai>=1.50",
    "google-genai>=0.5",
    "tavily-python>=0.5",
    "jinja2>=3.1",
    "rich>=13",
    "dataclasses-json>=0.6",
]

[project.scripts]
time-travel = "time_travel.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.23",
    "ruff>=0.4",
    "mypy>=1.10",
    "pre-commit>=3",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "I", "UP"]

[tool.mypy]
python_version = "3.10"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Create a virtual environment and install the package in dev mode**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Expected: `Successfully installed time-travel-premortem-1.0.0.dev0` (plus deps). May take 30–60 seconds.

- [ ] **Step 3: Verify the entry point is registered (even though the module doesn't exist yet)**

```bash
which time-travel
time-travel --help 2>&1 | head -5
```

Expected: `ModuleNotFoundError: No module named 'time_travel'` (the package is installed but `src/time_travel/cli.py` doesn't exist yet — that's fine for now). If you get "command not found", the venv is not active; re-run `source .venv/bin/activate`.

- [ ] **Step 4: Create package `__init__.py` files**

```bash
touch "/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/__init__.py"
touch "/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/providers/__init__.py"
touch "/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/render/__init__.py"
touch "/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/search/__init__.py"
touch "/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/personas/__init__.py"
touch "/Users/macbook/Documents/Chris developed Applications /time-travel/tests/__init__.py"
```

- [ ] **Step 5: Commit**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git add pyproject.toml src/ tests/__init__.py
git commit -m "feat: add pyproject.toml and package skeleton"
```

---

### Task 4: `models.py` — canonical Report dataclass (TDD)

**Files:**
- Create: `tests/test_models.py`
- Create: `src/time_travel/models.py`

- [ ] **Step 1: Write the failing tests**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/tests/test_models.py`:

```python
"""Tests for the canonical Report data model and JSON round-trip."""
from __future__ import annotations
import json
from datetime import datetime

import pytest


# ── helpers ────────────────────────────────────────────────────────────────────

def make_minimal_report():
    """Build the smallest valid Report for testing."""
    from time_travel.models import (
        BuriedRisk, EvidenceItem, InflatedRisk, Mitigation,
        PersonaActivation, Rebuttal, Report, Risk, SeverityScore, UserPOV,
    )
    return Report(
        plan_title="Test Plan",
        plan_source="inline",
        generated_at=datetime(2026, 5, 26, 14, 0, 0),
        horizons=["3mo", "6mo", "12mo"],
        plan_text="We will do the thing.",
        user_pov=UserPOV(
            thought_getting="Quick delivery",
            would_forgive="Minor delays",
            untrustworthy="Vague timeline",
            predictable_complaints="No updates",
        ),
        personas=[PersonaActivation(name="Skeptical Money", rationale="Always relevant")],
        narratives={
            "Skeptical Money": {
                "3mo": "Budget at risk",
                "6mo": "Overrun confirmed",
                "12mo": "Post-mortem being written",
            }
        },
        confirmed_risks=[
            Risk(
                id=1,
                name="Budget Overrun",
                severity=SeverityScore(trust=1, user_pain=0, blind_spot=2, ops_load=1, financial=3, strategic=2),
                likelihood="High",
                urgency="Block",
                tripwire="Burn rate > 120% in week 3",
                change_my_mind="Signed fixed-price vendor contract",
                mitigation="Add weekly budget review",
                owner_shape="Finance lead",
                citations=["Skeptical Money: POV on financial exposure"],
            )
        ],
        inflated_risks=[],
        buried_risks=[
            BuriedRisk(
                id=1,
                name="Founder burnout",
                why_unspoken="Nobody wants to name it",
                how_to_surface="Ask 'what does healthy pace look like in 12 months?'",
            )
        ],
        rebuttal=Rebuttal(
            agreements=["Budget risk is real"],
            disagreements=["Skeptical Money vs Frustrated End User on timeline: SM wants longer runway, FEU wants faster delivery"],
            cascades=["Budget overrun → team cuts → delivery slip. Severity uplift: High"],
        ),
        mitigations=[
            Mitigation(risk_id=1, action="Add weekly budget review", owner_shape="Finance lead", by="Week 1")
        ],
        revised_plan="We will do the thing. _[Mitigation for Risk #1: weekly budget review]_",
        evidence=[
            EvidenceItem(
                title="Example SaaS failure 2023",
                url="https://example.com/failure",
                when="2023",
                who="MidSize Corp",
                what_happened="Budget blew up in month 2",
                why_relevant="Same 90-day pattern",
            )
        ],
        unmitigated_confidence=40,
        mitigated_confidence=65,
        flags_used={"fast": False, "for_exec": False},
        process_log_path=None,
        exec_pager_path=None,
        ai_source=False,
        report_id="2026-05-26-1400-test-plan",
    )


# ── construction tests ──────────────────────────────────────────────────────────

def test_report_construction():
    report = make_minimal_report()
    assert report.plan_title == "Test Plan"
    assert report.unmitigated_confidence == 40
    assert report.mitigated_confidence == 65


def test_report_has_confirmed_risk():
    report = make_minimal_report()
    assert len(report.confirmed_risks) == 1
    risk = report.confirmed_risks[0]
    assert risk.name == "Budget Overrun"
    assert risk.severity.financial == 3
    assert risk.urgency == "Block"


def test_report_has_buried_risk():
    report = make_minimal_report()
    assert len(report.buried_risks) == 1
    assert report.buried_risks[0].name == "Founder burnout"


def test_report_narratives_structure():
    report = make_minimal_report()
    assert "Skeptical Money" in report.narratives
    assert "3mo" in report.narratives["Skeptical Money"]
    assert report.narratives["Skeptical Money"]["6mo"] == "Overrun confirmed"


def test_severity_score_defaults_to_zero():
    from time_travel.models import SeverityScore
    s = SeverityScore()
    assert s.trust == 0
    assert s.financial == 0
    assert s.strategic == 0


def test_rebuttal_defaults_to_empty_lists():
    from time_travel.models import Rebuttal
    r = Rebuttal()
    assert r.agreements == []
    assert r.disagreements == []
    assert r.cascades == []


# ── JSON round-trip tests ───────────────────────────────────────────────────────

def test_report_to_json_is_valid_json():
    report = make_minimal_report()
    json_str = report.to_json()
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)
    assert parsed["plan_title"] == "Test Plan"


def test_report_json_round_trip_preserves_title():
    from time_travel.models import Report
    report = make_minimal_report()
    loaded = Report.from_json(report.to_json())
    assert loaded.plan_title == report.plan_title


def test_report_json_round_trip_preserves_risks():
    from time_travel.models import Report
    report = make_minimal_report()
    loaded = Report.from_json(report.to_json())
    assert len(loaded.confirmed_risks) == 1
    assert loaded.confirmed_risks[0].name == "Budget Overrun"
    assert loaded.confirmed_risks[0].severity.financial == 3


def test_report_json_round_trip_preserves_confidence():
    from time_travel.models import Report
    report = make_minimal_report()
    loaded = Report.from_json(report.to_json())
    assert loaded.unmitigated_confidence == 40
    assert loaded.mitigated_confidence == 65


def test_report_to_dict():
    report = make_minimal_report()
    d = report.to_dict()
    assert isinstance(d, dict)
    assert d["plan_title"] == "Test Plan"
    assert isinstance(d["confirmed_risks"], list)


def test_report_json_round_trip_preserves_datetime():
    from time_travel.models import Report
    report = make_minimal_report()
    loaded = Report.from_json(report.to_json())
    # After round-trip, generated_at should be parseable as the same moment.
    # dataclasses_json stores datetime as ISO string.
    assert loaded.generated_at == report.generated_at or str(loaded.generated_at) == str(report.generated_at)
```

- [ ] **Step 2: Run the tests and confirm they all fail with ImportError**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/test_models.py -v 2>&1 | head -30
```

Expected: All tests fail with `ModuleNotFoundError: No module named 'time_travel.models'`

- [ ] **Step 3: Implement `models.py`**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/models.py`:

```python
"""Canonical Report data model.

All phases of the orchestrator produce one Report instance. Both
HTML and Markdown renderers consume it. The model is JSON-serializable
so `time-travel render report.json` can re-render without LLM calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class SeverityScore:
    """Six-axis severity score (each axis 0-3).

    T: Trust damage   U: User pain     B: Blind-spot
    O: Ops load       F: Financial     S: Strategic
    """
    trust: int = 0
    user_pain: int = 0
    blind_spot: int = 0
    ops_load: int = 0
    financial: int = 0
    strategic: int = 0


@dataclass_json
@dataclass
class Risk:
    """A Confirmed risk — evidence-backed, with full metadata."""
    id: int
    name: str
    severity: SeverityScore
    likelihood: str           # "Low" | "Medium" | "High"
    urgency: str              # "Block" | "Patch-fast" | "Monitor"
    tripwire: str             # first observable field signal
    change_my_mind: str       # evidence that would reduce confidence in this risk
    mitigation: str           # concrete action available this week
    owner_shape: str          # type of role that would own this
    citations: list[str] = field(default_factory=list)


@dataclass_json
@dataclass
class InflatedRisk:
    """A risk that sounds scary but downgrades on inspection."""
    id: int
    name: str
    why_downgraded: str


@dataclass_json
@dataclass
class BuriedRisk:
    """A risk that is politically unspoken; no one wants to name it."""
    id: int
    name: str
    why_unspoken: str
    how_to_surface: str


@dataclass_json
@dataclass
class UserPOV:
    """User-side reality captured before adversarial work begins."""
    thought_getting: str       # what users thought they were getting
    would_forgive: str         # what they'd forgive if things went sideways
    untrustworthy: str         # what would feel untrustworthy to them
    predictable_complaints: str  # predictable complaints in support / NPS


@dataclass_json
@dataclass
class PersonaActivation:
    """A persona selected for this run, with its selection rationale."""
    name: str
    rationale: str


@dataclass_json
@dataclass
class Rebuttal:
    """Output of the rebuttal round (Phase 3.5)."""
    agreements: list[str] = field(default_factory=list)
    # Each entry: "PersonaA vs PersonaB on <topic>: <summary>"
    disagreements: list[str] = field(default_factory=list)
    # Each entry: "<name>: <chain>. Severity uplift: Low|Medium|High"
    cascades: list[str] = field(default_factory=list)


@dataclass_json
@dataclass
class Mitigation:
    """A concrete mitigation action for a Confirmed risk."""
    risk_id: int
    action: str
    owner_shape: str
    by: str  # date or milestone string, e.g. "Week 1" or "2026-06-15"


@dataclass_json
@dataclass
class EvidenceItem:
    """A real-world analogue case from the evidence pack."""
    title: str
    url: str
    when: str
    who: str
    what_happened: str
    why_relevant: str


@dataclass_json
@dataclass
class Report:
    """The canonical output of one complete premortem run.

    Produced by Phase 4 synthesis. Both HTML and Markdown renderers
    consume this dataclass. It is JSON-serializable so reports can be
    re-rendered without re-running the LLM pipeline.
    """
    # ── metadata ──────────────────────────────────────────────────────────
    plan_title: str
    plan_source: str           # file path or "inline"
    generated_at: datetime
    horizons: list[str]        # e.g. ["3mo", "6mo", "12mo"]
    plan_text: str             # verbatim original plan

    # ── phase outputs ─────────────────────────────────────────────────────
    user_pov: UserPOV
    personas: list[PersonaActivation]
    # narratives: persona_name -> horizon -> narrative text
    narratives: dict[str, dict[str, str]]

    confirmed_risks: list[Risk]
    inflated_risks: list[InflatedRisk]
    buried_risks: list[BuriedRisk]

    rebuttal: Rebuttal
    mitigations: list[Mitigation]
    revised_plan: str          # original plan with injected mitigations
    evidence: list[EvidenceItem]

    # ── synthesis scores ──────────────────────────────────────────────────
    unmitigated_confidence: int   # 0-100
    mitigated_confidence: int     # 0-100

    # ── run metadata ──────────────────────────────────────────────────────
    flags_used: dict = field(default_factory=dict)
    process_log_path: Optional[str] = None
    exec_pager_path: Optional[str] = None
    ai_source: bool = False
    report_id: str = ""        # "YYYY-MM-DD-HHMM-<slug>"
```

- [ ] **Step 4: Run the tests and confirm they all pass**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/test_models.py -v
```

Expected output (all green):
```
tests/test_models.py::test_report_construction PASSED
tests/test_models.py::test_report_has_confirmed_risk PASSED
tests/test_models.py::test_report_has_buried_risk PASSED
tests/test_models.py::test_report_narratives_structure PASSED
tests/test_models.py::test_severity_score_defaults_to_zero PASSED
tests/test_models.py::test_rebuttal_defaults_to_empty_lists PASSED
tests/test_models.py::test_report_to_json_is_valid_json PASSED
tests/test_models.py::test_report_json_round_trip_preserves_title PASSED
tests/test_models.py::test_report_json_round_trip_preserves_risks PASSED
tests/test_models.py::test_report_json_round_trip_preserves_confidence PASSED
tests/test_models.py::test_report_to_dict PASSED
tests/test_models.py::test_report_json_round_trip_preserves_datetime PASSED
12 passed in X.XXs
```

If `test_report_json_round_trip_preserves_datetime` fails: `dataclasses_json` may not auto-handle `datetime`. If so, add a custom encoder/decoder to the `generated_at` field:

```python
from dataclasses_json import config as dcj_config
from marshmallow import fields as mm_fields

# In the Report dataclass, replace:
generated_at: datetime

# With:
generated_at: datetime = field(
    metadata=dcj_config(
        encoder=datetime.isoformat,
        decoder=datetime.fromisoformat,
        mm_field=mm_fields.DateTime(format="iso"),
    )
)
```

Re-run until all 12 pass.

- [ ] **Step 5: Commit**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git add src/time_travel/models.py tests/test_models.py
git commit -m "feat: add canonical Report data model with JSON round-trip

Implements Report + SeverityScore, Risk, InflatedRisk, BuriedRisk,
UserPOV, PersonaActivation, Rebuttal, Mitigation, EvidenceItem.
All types are dataclasses_json-decorated for JSON serialization.
12 tests covering construction and round-trip."
```

---

### Task 5: `providers/base.py` — LLMProvider ABC (TDD)

**Files:**
- Create: `tests/test_provider_base.py`
- Create: `src/time_travel/providers/base.py`

- [ ] **Step 1: Write the failing tests**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/tests/test_provider_base.py`:

```python
"""Tests for the LLMProvider abstract base class.

We test it by creating a minimal concrete subclass (ConcreteProvider)
and verifying the interface contract. We also verify that instantiating
the ABC directly raises TypeError.
"""
from __future__ import annotations
import asyncio
import pytest


# ── minimal concrete implementation for tests ──────────────────────────────────

class ConcreteProvider:
    """Built inline here so the test file has zero Plan-B dependencies."""

    @property
    def default_model(self) -> str:
        return "test-model-v1"

    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        return f"reply:{prompt[:20]}"

    async def complete_parallel(self, calls: list[dict]) -> list[str]:
        return [await self.complete(c["prompt"]) for c in calls]


# ── import the ABC ──────────────────────────────────────────────────────────────

def get_abc():
    from time_travel.providers.base import LLMProvider
    return LLMProvider


# ── tests ───────────────────────────────────────────────────────────────────────

def test_cannot_instantiate_abc_directly():
    LLMProvider = get_abc()
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        LLMProvider()


def test_concrete_subclass_satisfies_interface():
    LLMProvider = get_abc()

    class GoodProvider(LLMProvider):
        @property
        def default_model(self) -> str:
            return "good-model"

        async def complete(self, prompt, system=None, model=None, max_tokens=4096) -> str:
            return "ok"

        async def complete_parallel(self, calls: list[dict]) -> list[str]:
            return ["ok" for _ in calls]

    p = GoodProvider()
    assert p.default_model == "good-model"


def test_concrete_subclass_missing_complete_raises():
    LLMProvider = get_abc()

    with pytest.raises(TypeError):
        class BadProvider(LLMProvider):
            @property
            def default_model(self) -> str:
                return "m"
            # missing complete and complete_parallel

        BadProvider()


def test_complete_returns_string():
    p = ConcreteProvider()
    result = asyncio.run(p.complete("hello world"))
    assert isinstance(result, str)
    assert "reply:" in result


def test_complete_parallel_returns_list_of_strings():
    p = ConcreteProvider()
    calls = [
        {"prompt": "prompt one", "system": None},
        {"prompt": "prompt two", "system": None},
        {"prompt": "prompt three", "system": None},
    ]
    results = asyncio.run(p.complete_parallel(calls))
    assert len(results) == 3
    assert all(isinstance(r, str) for r in results)


def test_complete_parallel_preserves_order():
    """Results must map 1:1 to calls by position."""
    class IndexProvider:
        @property
        def default_model(self) -> str:
            return "m"
        async def complete(self, prompt, **_) -> str:
            return prompt  # echo
        async def complete_parallel(self, calls: list[dict]) -> list[str]:
            return [await self.complete(c["prompt"]) for c in calls]

    p = IndexProvider()
    calls = [{"prompt": f"call-{i}"} for i in range(5)]
    results = asyncio.run(p.complete_parallel(calls))
    assert results == [f"call-{i}" for i in range(5)]
```

- [ ] **Step 2: Run tests and confirm they fail**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/test_provider_base.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'time_travel.providers.base'`

- [ ] **Step 3: Implement `providers/base.py`**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/providers/base.py`:

```python
"""Abstract base class for LLM provider adapters.

All provider adapters (anthropic_provider, openai_provider, gemini_provider)
implement this interface. The orchestrator calls only these two methods —
it has no knowledge of which provider is active.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface for an LLM provider adapter.

    Usage:
        provider = AnthropicProvider(api_key=os.environ["ANTHROPIC_API_KEY"])
        result = await provider.complete("What's the risk here?")
        results = await provider.complete_parallel([
            {"prompt": "persona A prompt"},
            {"prompt": "persona B prompt"},
        ])
    """

    @property
    @abstractmethod
    def default_model(self) -> str:
        """The model identifier used when --model is not specified."""
        ...

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        """Run one completion and return the response text.

        Args:
            prompt: The user-turn content.
            system: Optional system prompt.
            model: Model override. Uses self.default_model if None.
            max_tokens: Maximum tokens in the response.

        Returns:
            The model's response as a plain string.
        """
        ...

    @abstractmethod
    async def complete_parallel(
        self,
        calls: list[dict],
    ) -> list[str]:
        """Run multiple completions in parallel and return results in order.

        Args:
            calls: List of dicts. Each dict may contain:
                   "prompt" (required), "system" (optional), "model" (optional),
                   "max_tokens" (optional).

        Returns:
            List of response strings, same length and order as `calls`.
        """
        ...
```

- [ ] **Step 4: Run tests and confirm they all pass**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/test_provider_base.py -v
```

Expected (all green):
```
tests/test_provider_base.py::test_cannot_instantiate_abc_directly PASSED
tests/test_provider_base.py::test_concrete_subclass_satisfies_interface PASSED
tests/test_provider_base.py::test_concrete_subclass_missing_complete_raises PASSED
tests/test_provider_base.py::test_complete_returns_string PASSED
tests/test_provider_base.py::test_complete_parallel_returns_list_of_strings PASSED
tests/test_provider_base.py::test_complete_parallel_preserves_order PASSED
6 passed in X.XXs
```

- [ ] **Step 5: Commit**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git add src/time_travel/providers/base.py tests/test_provider_base.py
git commit -m "feat: add LLMProvider ABC

Defines the two-method interface (complete, complete_parallel) that
all provider adapters implement. 6 tests covering instantiation, interface
satisfaction, and output contracts."
```

---

### Task 6: `cli.py` — argument parsing (TDD)

**Files:**
- Create: `tests/test_cli.py`
- Create: `src/time_travel/cli.py`

- [ ] **Step 1: Write the failing tests**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/tests/test_cli.py`:

```python
"""Tests for CLI argument parsing.

Tests verify that all flags parse correctly and that defaults match
the spec. No engine calls happen in these tests — all subcommands
in the skeleton raise NotImplementedError or print a stub message.
"""
from __future__ import annotations
import sys
import pytest
from unittest.mock import patch


def get_parser():
    from time_travel.cli import create_parser
    return create_parser()


# ── run command ─────────────────────────────────────────────────────────────────

def test_run_no_source_sets_source_none():
    args = get_parser().parse_args(["run"])
    assert args.command == "run"
    assert args.source is None


def test_run_with_file_path():
    args = get_parser().parse_args(["run", "my-plan.md"])
    assert args.source == "my-plan.md"


def test_run_provider_flag():
    args = get_parser().parse_args(["run", "--provider", "openai"])
    assert args.provider == "openai"


def test_run_provider_defaults_to_none():
    args = get_parser().parse_args(["run"])
    assert args.provider is None


def test_run_model_defaults_to_none():
    args = get_parser().parse_args(["run"])
    assert args.model is None


def test_run_search_default():
    args = get_parser().parse_args(["run"])
    assert args.search == "tavily"


def test_run_fast_flag():
    args = get_parser().parse_args(["run", "--fast"])
    assert args.fast is True


def test_run_fast_default_false():
    args = get_parser().parse_args(["run"])
    assert args.fast is False


def test_run_horizons_default():
    args = get_parser().parse_args(["run"])
    assert args.horizons == "3mo,6mo,12mo"


def test_run_horizons_override():
    args = get_parser().parse_args(["run", "--horizons", "1mo,3mo,1y"])
    assert args.horizons == "1mo,3mo,1y"


def test_run_output_default():
    args = get_parser().parse_args(["run"])
    assert args.output == "./time-travel-reports"


def test_run_output_override():
    args = get_parser().parse_args(["run", "--output", "/tmp/reports"])
    assert args.output == "/tmp/reports"


def test_run_for_exec_flag():
    args = get_parser().parse_args(["run", "--for-exec"])
    assert args.for_exec is True


def test_run_ai_source_flag():
    args = get_parser().parse_args(["run", "--ai-source"])
    assert args.ai_source is True


def test_run_no_process_log_flag():
    args = get_parser().parse_args(["run", "--no-process-log"])
    assert args.no_process_log is True


def test_run_combined_flags():
    args = get_parser().parse_args([
        "run", "plan.md",
        "--provider", "anthropic",
        "--model", "claude-opus-4-5",
        "--fast",
        "--for-exec",
        "--output", "/tmp/out",
    ])
    assert args.source == "plan.md"
    assert args.provider == "anthropic"
    assert args.model == "claude-opus-4-5"
    assert args.fast is True
    assert args.for_exec is True
    assert args.output == "/tmp/out"


# ── render command ───────────────────────────────────────────────────────────────

def test_render_requires_json_path():
    args = get_parser().parse_args(["render", "report.json"])
    assert args.command == "render"
    assert args.report_json == "report.json"


def test_render_output_default():
    args = get_parser().parse_args(["render", "report.json"])
    assert args.output == "./time-travel-reports"


# ── doctor command ───────────────────────────────────────────────────────────────

def test_doctor_command_parses():
    args = get_parser().parse_args(["doctor"])
    assert args.command == "doctor"


# ── personas command ─────────────────────────────────────────────────────────────

def test_personas_list_parses():
    args = get_parser().parse_args(["personas", "list"])
    assert args.command == "personas"
    assert args.personas_cmd == "list"


# ── no command exits with code 1 ─────────────────────────────────────────────────

def test_no_command_exits_with_code_1():
    with patch("sys.argv", ["time-travel"]):
        with pytest.raises(SystemExit) as exc:
            from time_travel.cli import main
            main()
    assert exc.value.code == 1
```

- [ ] **Step 2: Run tests and confirm they fail**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/test_cli.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'time_travel.cli'`

- [ ] **Step 3: Implement `cli.py`**

Create `/Users/macbook/Documents/Chris developed Applications /time-travel/src/time_travel/cli.py`:

```python
"""CLI entry point for time-travel.

All subcommands are stubbed in Plan A. The orchestrator (Plan B) and
renderers (Plan C) will replace the NotImplementedError raises with
real dispatch.
"""
from __future__ import annotations

import argparse
import sys


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="time-travel",
        description="Multi-agent premortem for plans. Sends personas to the future, brings back risks.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── run ───────────────────────────────────────────────────────────────────
    run = subparsers.add_parser("run", help="Run a premortem on a plan")
    run.add_argument(
        "source",
        nargs="?",
        default=None,
        help="Plan file path or inline text. Omit for auto-detect.",
    )
    run.add_argument("--provider", default=None, help="LLM provider: anthropic|openai|gemini")
    run.add_argument("--model", default=None, help="Model override (provider-specific name)")
    run.add_argument("--search", default="tavily", help="Web search provider (default: tavily)")
    run.add_argument("--fast", action="store_true", help="Skip parallel dispatch (lower quality, ~20%% cost)")
    run.add_argument("--horizons", default="3mo,6mo,12mo", help="Comma-separated horizon list")
    run.add_argument("--output", default="./time-travel-reports", help="Output directory for artifacts")
    run.add_argument("--for-exec", action="store_true", dest="for_exec", help="Also emit ≤300-word exec one-pager")
    run.add_argument("--ai-source", action="store_true", dest="ai_source", help="Flag plan as AI-authored")
    run.add_argument("--no-process-log", action="store_true", dest="no_process_log", help="Skip process log artifact")

    # ── render ────────────────────────────────────────────────────────────────
    render = subparsers.add_parser("render", help="Re-render from a saved JSON report (no LLM calls)")
    render.add_argument("report_json", help="Path to a report JSON file")
    render.add_argument("--output", default="./time-travel-reports", help="Output directory")

    # ── doctor ────────────────────────────────────────────────────────────────
    subparsers.add_parser("doctor", help="Verify env vars, installed deps, and network connectivity")

    # ── personas ──────────────────────────────────────────────────────────────
    personas = subparsers.add_parser("personas", help="Inspect the built-in persona roster")
    personas_sub = personas.add_subparsers(dest="personas_cmd")
    personas_sub.add_parser("list", help="List all personas with their domain tags")

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        # Implemented in Plan B (orchestrator.py)
        raise NotImplementedError(
            "Engine not yet installed. Run Plan B to implement the orchestrator."
        )

    elif args.command == "render":
        # Implemented in Plan C (renderers)
        raise NotImplementedError(
            "Renderer not yet installed. Run Plan C to implement the renderers."
        )

    elif args.command == "doctor":
        print("doctor: checks not yet implemented (Plan B)")

    elif args.command == "personas":
        if args.personas_cmd == "list":
            print("personas list: not yet implemented (Plan B)")
        else:
            parser.parse_args(["personas", "--help"])


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests and confirm all pass**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/test_cli.py -v
```

Expected (all green, 21 tests):
```
tests/test_cli.py::test_run_no_source_sets_source_none PASSED
tests/test_cli.py::test_run_with_file_path PASSED
... (18 more)
tests/test_cli.py::test_no_command_exits_with_code_1 PASSED
21 passed in X.XXs
```

- [ ] **Step 5: Verify `time-travel --help` works from the shell**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
time-travel --help
```

Expected:
```
usage: time-travel [-h] {run,render,doctor,personas} ...

Multi-agent premortem for plans. Sends personas to the future, brings back risks.

positional arguments:
  {run,render,doctor,personas}
    run                 Run a premortem on a plan
    render              Re-render from a saved JSON report (no LLM calls)
    doctor              Verify env vars, installed deps, and network connectivity
    personas            Inspect the built-in persona roster

options:
  -h, --help            show this help message and exit
```

- [ ] **Step 6: Run the full test suite to confirm nothing regressed**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/ -v
```

Expected: 39 passed (12 models + 6 provider_base + 21 cli).

- [ ] **Step 7: Commit**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git add src/time_travel/cli.py tests/test_cli.py
git commit -m "feat: add CLI argument parser with all flags

Implements create_parser() + main() with all subcommands from the spec:
run (with all flags), render, doctor, personas list.
All subcommands are stubbed pending Plan B/C.
22 tests cover all flags and defaults."
```

---

### Task 7: Final wiring + CHANGELOG update

- [ ] **Step 1: Run `ruff` and fix any lint issues**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
ruff check src/ tests/
```

Expected: No output (no issues). If there are issues, run `ruff check --fix src/ tests/` to auto-fix safe issues, then inspect any remaining ones manually.

- [ ] **Step 2: Run `mypy` and note any type errors**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
mypy src/time_travel/
```

Expected: `Success: no issues found in 7 source files`

Common issue: `mypy` may complain about `dict` in `Report.flags_used` being untyped. Fix by changing `dict` to `dict[str, object]` in `models.py` if it errors.

- [ ] **Step 3: Update `CHANGELOG.md`**

Open `/Users/macbook/Documents/Chris developed Applications /time-travel/CHANGELOG.md` and prepend the following section (keep any existing content below it):

```markdown
## [1.0.0-dev] - 2026-05-26

### Added (Plan A — Foundation)
- Polyglot monorepo layout: `src/time_travel/`, `harnesses/`, `tests/`, `examples/`, `scripts/`
- Canonical `Report` dataclass with all sub-types and JSON round-trip (`models.py`)
- `LLMProvider` ABC defining the `complete` + `complete_parallel` interface (`providers/base.py`)
- Full CLI argument parser with all v1.0 flags: `run`, `render`, `doctor`, `personas list` (`cli.py`)
- Migrated existing Claude Code plugin to `harnesses/claude-code/plugins/time-travel/`
- Added Codex skill stub at `harnesses/codex/skills/time-travel/`
- 40 tests covering model construction, JSON round-trip, provider ABC, and CLI parsing

### Changed
- Moved `plugins/time-travel/` → `harnesses/claude-code/plugins/time-travel/` (content unchanged)

### Upcoming (Plans B/C/D)
- Plan B: Orchestrator, provider adapters (Anthropic/OpenAI/Gemini), Tavily search, persona library, synthesis
- Plan C: HTML + Markdown renderers
- Plan D: Thin harness SKILL.md wrappers, install script, GitHub Actions CI
```

- [ ] **Step 4: Final commit**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
source .venv/bin/activate
pytest tests/ -v   # confirm 39 passed
git add CHANGELOG.md
git commit -m "chore: update CHANGELOG for v1.0-dev Plan A"
```

- [ ] **Step 5: Push to remote**

```bash
cd "/Users/macbook/Documents/Chris developed Applications /time-travel"
git push -u origin main
```

If the remote had content and a different history, you may need:
```bash
git push --force-with-lease origin main
```

Only use `--force-with-lease` if you verified in Task 1 that the remote had only your own earlier work. If the remote has commits you haven't seen, `git pull --rebase origin main` first.

---

## Plan A complete — end state

After Task 7:
- `pip install -e ".[dev]"` succeeds
- `time-travel --help` shows all subcommands
- `time-travel run plan.md` raises `NotImplementedError` (expected — Plan B implements it)
- 40 tests pass (`pytest tests/ -v`)
- Remote branch is up to date

**Next:** Write and execute Plan B (orchestrator, providers, personas, synthesis) to make `time-travel run examples/sample-plan.md` produce a `Report` JSON.
