"""Render a Report as an executive one-pager (≤300 words), in Markdown and HTML."""
from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from time_travel.models import Report
from time_travel.synthesis import exec_summary_context

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
_MAX_WORDS = 300
_TAG_RE = re.compile(r"<[^>]+>")
_STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.DOTALL | re.IGNORECASE)


class ExecPagerTooLongError(ValueError):
    pass


def _context(report: Report) -> dict[str, object]:
    return exec_summary_context(
        report.unmitigated_confidence,
        report.mitigated_confidence,
        report.confirmed_risks,
        report.inflated_risks,
        report.buried_risks,
    )


def _check_word_limit(text: str) -> None:
    word_count = len(text.split())
    if word_count > _MAX_WORDS:
        raise ExecPagerTooLongError(f"Exec pager is {word_count} words (limit: {_MAX_WORDS})")


def render_exec(report: Report) -> str:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("exec.md.j2")
    text = template.render(report=report, **_context(report))
    _check_word_limit(text)
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
    html = template.render(report=report, **_context(report))
    visible_text = _TAG_RE.sub(" ", _STYLE_RE.sub(" ", html))
    _check_word_limit(visible_text)
    return html


def render_exec_html_to_file(report: Report, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_exec_html(report)
    output_path.write_text(html, encoding="utf-8")
    return output_path
