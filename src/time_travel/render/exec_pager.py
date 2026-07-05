"""Render a Report as an executive one-pager (≤300 words)."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from time_travel.models import Report
from time_travel.synthesis import confidence_render_context

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_MAX_WORDS = 300


class ExecPagerTooLongError(ValueError):
    pass


def _confidence_context(report: Report) -> dict[str, str]:
    return confidence_render_context(
        report.unmitigated_confidence, report.mitigated_confidence, report.confirmed_risks
    )


def render_exec(report: Report) -> str:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("exec.md.j2")
    text = template.render(report=report, **_confidence_context(report))
    word_count = len(text.split())
    if word_count > _MAX_WORDS:
        raise ExecPagerTooLongError(
            f"Exec pager is {word_count} words (limit: {_MAX_WORDS})"
        )
    return text


def render_exec_to_file(report: Report, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    md = render_exec(report)
    output_path.write_text(md, encoding="utf-8")
    return output_path


def render_exec_html(report: Report) -> str:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=True,
        keep_trailing_newline=True,
    )
    template = env.get_template("exec.html.j2")
    return template.render(report=report, **_confidence_context(report))


def render_exec_html_to_file(report: Report, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_exec_html(report)
    output_path.write_text(html, encoding="utf-8")
    return output_path
