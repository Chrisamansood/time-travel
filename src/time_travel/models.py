"""Canonical Report data model.

All phases of the orchestrator produce one Report instance. Both
HTML and Markdown renderers consume it. The model is JSON-serializable
so `time-travel render report.json` can re-render without LLM calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import config as dcj_config
from dataclasses_json import dataclass_json
from marshmallow import fields as mm_fields


@dataclass_json
@dataclass
class SeverityScore:
    """Six-axis severity score (each axis 0-3), per claims schema v1.

    Technical  Financial  Trust     User pain
    Ops load   Strategic
    """
    technical: int = 0
    financial: int = 0
    trust: int = 0
    user_pain: int = 0
    ops_load: int = 0
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
    mitigation_summary: str   # one-line action summary (full detail in Mitigation class)
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
    thought_getting: str
    would_forgive: str
    untrustworthy: str
    predictable_complaints: str


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
    disagreements: list[str] = field(default_factory=list)
    cascades: list[str] = field(default_factory=list)


@dataclass_json
@dataclass
class Mitigation:
    """A concrete mitigation action for a Confirmed risk."""
    risk_id: int
    action: str
    owner_shape: str
    by: str


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
    plan_source: str
    generated_at: datetime = field(
        metadata=dcj_config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=mm_fields.DateTime(format="iso"),
        )
    )
    horizons: list[str]
    plan_text: str

    # ── phase outputs ─────────────────────────────────────────────────────
    user_pov: UserPOV
    personas: list[PersonaActivation]
    narratives: dict[str, dict[str, str]]

    confirmed_risks: list[Risk]
    inflated_risks: list[InflatedRisk]
    buried_risks: list[BuriedRisk]

    rebuttal: Rebuttal
    mitigations: list[Mitigation]
    revised_plan: str
    evidence: list[EvidenceItem]

    # ── synthesis scores ──────────────────────────────────────────────────
    unmitigated_confidence: int
    mitigated_confidence: int

    # ── run metadata ──────────────────────────────────────────────────────
    flags_used: dict[str, bool] = field(default_factory=dict)
    process_log_path: str | None = None
    exec_pager_path: str | None = None
    ai_source: bool = False
    report_id: str = ""
