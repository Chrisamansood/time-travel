"""Snapshot tests for the HTML matrix renderer."""
from __future__ import annotations

from pathlib import Path

from time_travel.models import Report
from time_travel.render.html_matrix import render_html, render_html_to_file

_FIXTURES = Path(__file__).resolve().parent.parent / "examples"
_GOLDEN = _FIXTURES / "sample-report.html"
_FIXTURE_JSON = _FIXTURES / "sample-report.json"


def _load_fixture() -> Report:
    return Report.from_json(_FIXTURE_JSON.read_text())


def test_render_html_matches_golden(request):
    report = _load_fixture()
    html = render_html(report)
    if request.config.getoption("--update-golden"):
        _GOLDEN.write_text(html, encoding="utf-8")
        return
    expected = _GOLDEN.read_text(encoding="utf-8")
    assert html == expected, "HTML output differs from golden file. Run pytest --update-golden to regenerate."


def test_render_html_contains_plan_title():
    report = _load_fixture()
    html = render_html(report)
    assert report.plan_title in html


def test_render_html_contains_all_confirmed_risks():
    report = _load_fixture()
    html = render_html(report)
    for risk in report.confirmed_risks:
        assert risk.name in html


def test_render_html_contains_confidence_bands_not_percentages():
    report = _load_fixture()
    html = render_html(report)
    assert ">Low<" in html
    assert ">Moderate<" in html
    assert f"{report.unmitigated_confidence}%" not in html
    assert f"{report.mitigated_confidence}%" not in html


def test_render_html_contains_footer_watermark():
    html = render_html(_load_fixture())
    assert "Chris Sood" in html
    assert "Agentic AI Strategy" in html
    assert "https://x.com/Sood_Chris" in html
    assert "https://chrisamansood.medium.com/" in html
    assert "https://www.linkedin.com/in/chrisamansood/" in html


def test_render_html_contains_tab_controls():
    html = render_html(_load_fixture())
    assert "CONFIRMED" in html
    assert "INFLATED" in html
    assert "BURIED" in html


def test_render_html_contains_personas():
    report = _load_fixture()
    html = render_html(report)
    for p in report.personas:
        assert p.name in html


def test_render_html_contains_user_pov():
    report = _load_fixture()
    html = render_html(report)
    assert report.user_pov.thought_getting in html
    assert report.user_pov.would_forgive in html


def test_render_html_contains_mitigations():
    report = _load_fixture()
    html = render_html(report)
    for m in report.mitigations:
        assert m.action in html


def test_render_html_contains_evidence():
    report = _load_fixture()
    html = render_html(report)
    for e in report.evidence:
        assert e.title in html


def test_render_html_contains_narrow_screen_notice():
    html = render_html(_load_fixture())
    assert "BEST VIEWED" in html


def test_render_html_self_contained():
    html = render_html(_load_fixture())
    assert "<style>" in html
    assert "<script>" in html
    assert "cdn" not in html.lower()


def test_render_html_has_exec_summary_with_tldr_and_top_risks():
    report = _load_fixture()
    html = render_html(report)
    assert "EXEC SUMMARY" in html
    assert "TOP RISKS" in html
    ranked = report.confirmed_risks[:3]
    for risk in ranked:
        # top risk names appear before the collapsible "Full report" section
        assert html.index(risk.name) < html.index("Full report")


def test_render_html_exec_summary_shows_one_buried_risk():
    report = _load_fixture()
    html = render_html(report)
    if report.buried_risks:
        assert "BURIED RISK" in html
        assert html.index(report.buried_risks[0].name) < html.index("Full report")


def test_render_html_wraps_full_detail_in_collapsible_details():
    html = render_html(_load_fixture())
    assert "<details" in html
    assert "<summary>" in html


def test_render_html_no_line_over_2000_chars():
    html = render_html(_load_fixture())
    longest = max(len(line) for line in html.splitlines())
    assert longest <= 2000, f"longest line is {longest} chars"


def test_render_html_to_file(tmp_path):
    report = _load_fixture()
    out = tmp_path / "output" / "report.html"
    result = render_html_to_file(report, out)
    assert result == out
    assert out.exists()
    content = out.read_text()
    assert report.plan_title in content
