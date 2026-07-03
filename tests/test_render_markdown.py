"""Snapshot tests for the Markdown renderer."""
from __future__ import annotations

from pathlib import Path

from time_travel.models import Report
from time_travel.render.markdown import render_markdown, render_markdown_to_file

_FIXTURES = Path(__file__).resolve().parent.parent / "examples"
_GOLDEN = _FIXTURES / "sample-report.md"
_FIXTURE_JSON = _FIXTURES / "sample-report.json"


def _load_fixture() -> Report:
    return Report.from_json(_FIXTURE_JSON.read_text())


def test_render_markdown_matches_golden(request):
    report = _load_fixture()
    md = render_markdown(report)
    if request.config.getoption("--update-golden"):
        _GOLDEN.write_text(md, encoding="utf-8")
        return
    expected = _GOLDEN.read_text(encoding="utf-8")
    assert md == expected


def test_render_markdown_contains_plan_title():
    md = render_markdown(_load_fixture())
    assert "Launch a SaaS MVP in 90 Days" in md


def test_render_markdown_contains_confidence():
    md = render_markdown(_load_fixture())
    assert "35%" in md
    assert "62%" in md


def test_render_markdown_contains_all_sections():
    md = render_markdown(_load_fixture())
    for section in ["User POV", "Personas", "Confirmed Risks", "Inflated Risks",
                     "Buried Risks", "Rebuttal", "Mitigations", "Evidence", "Methodology"]:
        assert f"## {section}" in md


def test_render_markdown_contains_footer():
    md = render_markdown(_load_fixture())
    assert "Chris Sood" in md
    assert "x.com/Sood_Chris" in md


def test_render_markdown_to_file(tmp_path):
    report = _load_fixture()
    out = tmp_path / "output" / "report.md"
    result = render_markdown_to_file(report, out)
    assert result == out
    assert out.exists()
    assert report.plan_title in out.read_text()
