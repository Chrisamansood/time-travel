"""End-to-end tests for the orchestrator — stub provider, no live network."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from time_travel.models import Rebuttal, Report, UserPOV
from time_travel.orchestrator import (
    RunOptions,
    _resolve_provider,
    _resolve_search,
    render_from_json,
    run,
)
from time_travel.providers.stub_provider import StubProvider
from time_travel.search.base import SearchResult, WebSearch

PLAN_TEXT = (
    "We will replace the support team with an AI agent to cut costs by 40%. "
    "This is a seamless, transformational, end-to-end solution."
)


class FakeSearch(WebSearch):
    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        return [
            SearchResult(
                title="A relevant case study",
                url="https://example.com/case",
                snippet="A company tried something similar and it went sideways.",
                score=0.9,
            )
        ]


@pytest.fixture
def opts(tmp_path):
    return RunOptions(output=str(tmp_path))


@pytest.fixture
def provider():
    return StubProvider()


@pytest.fixture
def search():
    return FakeSearch()


@pytest.mark.asyncio
async def test_run_produces_a_valid_report(opts, provider, search):
    report = await run(PLAN_TEXT, opts, provider=provider, search=search)

    assert isinstance(report, Report)
    assert report.plan_text == PLAN_TEXT
    assert len(report.personas) >= 1


@pytest.mark.asyncio
async def test_run_populates_user_pov_from_provider_response(opts, provider, search):
    report = await run(PLAN_TEXT, opts, provider=provider, search=search)

    assert report.user_pov.thought_getting == "A fast product"


@pytest.mark.asyncio
async def test_run_confidence_scores_within_bounds(opts, provider, search):
    report = await run(PLAN_TEXT, opts, provider=provider, search=search)

    assert 0 <= report.unmitigated_confidence <= 100
    assert 0 <= report.mitigated_confidence <= 100


@pytest.mark.asyncio
async def test_run_writes_report_json_html_and_markdown(opts, provider, search):
    await run(PLAN_TEXT, opts, provider=provider, search=search)

    out_dir = next(Path(opts.output).iterdir())
    assert (out_dir / "report.json").exists()
    assert (out_dir / "report.html").exists()
    assert (out_dir / "report.md").exists()

    saved = json.loads((out_dir / "report.json").read_text())
    assert saved["plan_title"]


@pytest.mark.asyncio
async def test_run_writes_exec_md_only_when_for_exec_flag_set(tmp_path, provider, search):
    opts_with_exec = RunOptions(output=str(tmp_path / "with"), for_exec=True)
    opts_without_exec = RunOptions(output=str(tmp_path / "without"), for_exec=False)

    await run(PLAN_TEXT, opts_with_exec, provider=provider, search=search)
    await run(PLAN_TEXT, opts_without_exec, provider=provider, search=search)

    with_dir = next(Path(opts_with_exec.output).iterdir())
    without_dir = next(Path(opts_without_exec.output).iterdir())
    assert (with_dir / "exec.md").exists()
    assert not (without_dir / "exec.md").exists()


@pytest.mark.asyncio
async def test_run_sets_flags_used_from_options(opts, provider, search):
    opts.fast = True
    opts.ai_source = True

    report = await run(PLAN_TEXT, opts, provider=provider, search=search)

    assert report.flags_used["fast"] is True
    assert report.flags_used["ai_source"] is True


@pytest.mark.asyncio
async def test_run_reads_plan_text_from_file(tmp_path, provider, search):
    plan_file = tmp_path / "my-plan.md"
    plan_file.write_text(PLAN_TEXT, encoding="utf-8")
    file_opts = RunOptions(output=str(tmp_path / "out"))

    report = await run(str(plan_file), file_opts, provider=provider, search=search)

    assert report.plan_text == PLAN_TEXT
    assert report.plan_title != "Untitled Plan"


@pytest.mark.asyncio
async def test_run_skips_process_log_when_flag_set(opts, provider, search):
    opts.no_process_log = True

    report = await run(PLAN_TEXT, opts, provider=provider, search=search)

    assert report.process_log_path is None


def test_render_from_json_rerenders_without_a_provider(tmp_path):
    report = Report(
        plan_title="Test Plan",
        plan_source="inline",
        generated_at=datetime(2026, 1, 1),
        horizons=["3mo", "6mo", "12mo"],
        plan_text="Some plan",
        user_pov=UserPOV("", "", "", ""),
        personas=[],
        narratives={},
        confirmed_risks=[],
        inflated_risks=[],
        buried_risks=[],
        rebuttal=Rebuttal([], [], []),
        mitigations=[],
        revised_plan="Some plan",
        evidence=[],
        unmitigated_confidence=100,
        mitigated_confidence=100,
        report_id="20260101T000000",
    )
    json_path = tmp_path / "report.json"
    json_path.write_text(report.to_json(), encoding="utf-8")

    out_dir = render_from_json(str(json_path), str(tmp_path / "rendered"))

    assert (out_dir / "report.html").exists()
    assert (out_dir / "report.md").exists()


class TestResolveProvider:
    def test_stub_flag_resolves_to_stub_provider_no_network(self):
        provider = _resolve_provider(RunOptions(provider="stub"))
        assert isinstance(provider, StubProvider)


class TestResolveSearch:
    def test_stub_flag_does_not_resolve_to_tavily(self):
        from time_travel.search.tavily import TavilySearch

        search = _resolve_search(RunOptions(search="stub"))
        assert not isinstance(search, TavilySearch)

    @pytest.mark.asyncio
    async def test_stub_search_client_returns_deterministic_canned_result(self):
        search = _resolve_search(RunOptions(search="stub"))
        results = await search.search("anything")
        assert results == await search.search("anything")
        assert all(isinstance(r, SearchResult) for r in results)
