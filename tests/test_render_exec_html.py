"""Tests for the exec.html one-pager renderer (T4: exec-first HTML output)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from time_travel.models import BuriedRisk, Mitigation, Report, Risk, SeverityScore
from time_travel.render.exec_pager import (
    ExecPagerTooLongError,
    render_exec_html,
    render_exec_html_to_file,
)

_FIXTURES = Path(__file__).resolve().parent.parent / "examples"
_FIXTURE_JSON = _FIXTURES / "sample-report.json"

_TAG_RE = re.compile(r"<[^>]+>")
_STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.DOTALL | re.IGNORECASE)


def _load_fixture() -> Report:
    return Report.from_json(_FIXTURE_JSON.read_text())


def _visible_word_count(html: str) -> int:
    text = _TAG_RE.sub(" ", _STYLE_RE.sub(" ", html))
    return len(text.split())


def test_render_exec_html_is_self_contained():
    html = render_exec_html(_load_fixture())
    assert "<style>" in html
    assert "cdn" not in html.lower()


def test_render_exec_html_within_word_limit():
    html = render_exec_html(_load_fixture())
    word_count = _visible_word_count(html)
    assert word_count <= 300, f"exec.html is {word_count} visible words (limit: 300)"


def test_render_exec_html_contains_plan_title_and_confidence_bands():
    report = _load_fixture()
    html = render_exec_html(report)
    assert report.plan_title in html
    assert "Low" in html
    assert "Moderate" in html
    assert f"{report.unmitigated_confidence}%" not in html
    assert f"{report.mitigated_confidence}%" not in html


def test_render_exec_html_contains_top_risks_and_buried_risk():
    report = _load_fixture()
    html = render_exec_html(report)
    for risk in report.confirmed_risks[:3]:
        assert risk.name in html
    if report.buried_risks:
        assert report.buried_risks[0].name in html


def test_render_exec_html_no_line_over_2000_chars():
    html = render_exec_html(_load_fixture())
    longest = max(len(line) for line in html.splitlines())
    assert longest <= 2000, f"longest line is {longest} chars"


def test_render_exec_html_enforces_word_limit():
    report = _load_fixture()
    long_name = "word " * 60
    report.confirmed_risks = [
        Risk(
            id=i, name=long_name, severity=SeverityScore(), likelihood="High",
            urgency="Block", tripwire="x", change_my_mind="x",
            mitigation_summary=long_name, owner_shape="x",
        )
        for i in range(20)
    ]
    report.mitigations = [
        Mitigation(risk_id=i, action=long_name, owner_shape="x", by="now") for i in range(20)
    ]
    report.buried_risks = [
        BuriedRisk(id=i, name=long_name, why_unspoken=long_name, how_to_surface="x")
        for i in range(20)
    ]

    with pytest.raises(ExecPagerTooLongError):
        render_exec_html(report)


def test_render_exec_html_to_file(tmp_path):
    report = _load_fixture()
    out = tmp_path / "output" / "exec.html"
    result = render_exec_html_to_file(report, out)
    assert result == out
    assert out.exists()
    assert report.plan_title in out.read_text()
