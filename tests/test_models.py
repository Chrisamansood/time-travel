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
    assert loaded.generated_at == report.generated_at or str(loaded.generated_at) == str(report.generated_at)
