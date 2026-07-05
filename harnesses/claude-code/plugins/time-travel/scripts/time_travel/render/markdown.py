"""Render a Report as a Markdown document."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from time_travel.models import Report
from time_travel.synthesis import confidence_render_context

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_markdown(report: Report) -> str:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("report.md.j2")
    context = confidence_render_context(
        report.unmitigated_confidence, report.mitigated_confidence, report.confirmed_risks
    )
    return template.render(report=report, **context)


def render_markdown_to_file(report: Report, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    md = render_markdown(report)
    output_path.write_text(md, encoding="utf-8")
    return output_path
