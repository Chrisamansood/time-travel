"""Snapshot tests for the exec pager renderer."""
from __future__ import annotations

from pathlib import Path

import pytest

from time_travel.models import Report
from time_travel.render.exec_pager import ExecPagerTooLongError, render_exec, render_exec_to_file

_FIXTURES = Path(__file__).resolve().parent.parent / "examples"
_GOLDEN = _FIXTURES / "sample-exec.md"
_FIXTURE_JSON = _FIXTURES / "sample-report.json"


def _load_fixture() -> Report:
    return Report.from_json(_FIXTURE_JSON.read_text())


def test_render_exec_matches_golden(request):
    report = _load_fixture()
    md = render_exec(report)
    if request.config.getoption("--update-golden"):
        _GOLDEN.write_text(md, encoding="utf-8")
        return
    expected = _GOLDEN.read_text(encoding="utf-8")
    assert md == expected


def test_render_exec_within_word_limit():
    md = render_exec(_load_fixture())
    word_count = len(md.split())
    assert word_count <= 300, f"Exec pager is {word_count} words (limit: 300)"


def test_render_exec_contains_plan_title():
    md = render_exec(_load_fixture())
    assert "Launch a SaaS MVP in 90 Days" in md


def test_render_exec_contains_confidence_bands_not_percentages():
    report = _load_fixture()
    md = render_exec(report)
    assert "Low" in md
    assert "Moderate" in md
    assert f"{report.unmitigated_confidence}%" not in md
    assert f"{report.mitigated_confidence}%" not in md


def test_render_exec_contains_top_risks():
    report = _load_fixture()
    md = render_exec(report)
    for risk in report.confirmed_risks[:5]:
        assert risk.name in md


def test_render_exec_enforces_word_limit():
    from time_travel.models import BuriedRisk, Mitigation, Risk, SeverityScore
    report = _load_fixture()
    long_name = "word " * 60
    report.confirmed_risks = [
        Risk(id=i, name=long_name, severity=SeverityScore(), likelihood="High",
             urgency="Block", tripwire="x", change_my_mind="x",
             mitigation_summary=long_name, owner_shape="x")
        for i in range(20)
    ]
    report.mitigations = [
        Mitigation(risk_id=i, action=long_name, owner_shape="x", by="now")
        for i in range(20)
    ]
    report.buried_risks = [
        BuriedRisk(id=i, name=long_name, why_unspoken=long_name, how_to_surface="x")
        for i in range(20)
    ]
    with pytest.raises(ExecPagerTooLongError):
        render_exec(report)


def test_render_exec_to_file(tmp_path):
    report = _load_fixture()
    out = tmp_path / "output" / "exec.md"
    result = render_exec_to_file(report, out)
    assert result == out
    assert out.exists()
    assert report.plan_title in out.read_text()
