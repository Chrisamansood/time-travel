"""Render a Report as a self-contained HTML matrix dashboard."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from time_travel.models import Report
from time_travel.synthesis import exec_summary_context

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_html(report: Report) -> str:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("report.html.j2")
    context = exec_summary_context(
        report.unmitigated_confidence,
        report.mitigated_confidence,
        report.confirmed_risks,
        report.inflated_risks,
        report.buried_risks,
    )
    return template.render(report=report, **context)


def render_html_to_file(report: Report, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_html(report)
    output_path.write_text(html, encoding="utf-8")
    return output_path
