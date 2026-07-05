"""Orchestrator — six-phase premortem pipeline wiring all Plan B modules.

Phase 0: Ingest plan text
Phase 1: User-POV + blind-spot candidates — single LLM call
Phase 2: Persona roster selection + evidence gathering
Phase 3: Persona fan-out — parallel LLM calls
Phase 3.5: Rebuttal round — single LLM call
Phase 4: Synthesis — classify risks, score confidence, revise plan
Phase 5: Render artifacts (report.json/.html/.md, exec.md if requested)
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from time_travel.models import (
    BuriedRisk,
    EvidenceItem,
    Mitigation,
    PersonaActivation,
    Rebuttal,
    Report,
    SeverityScore,
    UserPOV,
)
from time_travel.personas.library import Persona
from time_travel.personas.selection import select_roster
from time_travel.providers.base import LLMProvider
from time_travel.render.exec_pager import render_exec_to_file
from time_travel.render.html_matrix import render_html_to_file
from time_travel.render.markdown import render_markdown_to_file
from time_travel.search.base import WebSearch
from time_travel.synthesis import PersonaRiskClaim, classify_risks, compute_confidence


@dataclass
class RunOptions:
    provider: str | None = None
    model: str | None = None
    search: str = "tavily"
    fast: bool = False
    horizons: str = "3mo,6mo,12mo"
    output: str = "./time-travel-reports"
    for_exec: bool = False
    ai_source: bool = False
    no_process_log: bool = False


def _try_json(text: str) -> dict[str, Any] | list[Any] | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        result = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(result, (dict, list)):
        return result
    return None


def _ingest_plan(source: str | None) -> tuple[str, str]:
    """Return (plan_title, plan_text)."""
    if source is None:
        text = sys.stdin.read() if not sys.stdin.isatty() else ""
        return "Untitled Plan", text

    path = Path(source)
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        title = path.stem.replace("-", " ").replace("_", " ").title()
        return title, text

    stripped = source.strip()
    first_line = stripped.splitlines()[0] if stripped else "Untitled Plan"
    return first_line[:60], source


def _resolve_provider(opts: RunOptions) -> LLMProvider:
    name = opts.provider or os.environ.get("TIME_TRAVEL_PROVIDER")
    if name is None:
        if os.environ.get("ANTHROPIC_API_KEY"):
            name = "anthropic"
        elif os.environ.get("OPENAI_API_KEY"):
            name = "openai"
        elif os.environ.get("GEMINI_API_KEY"):
            name = "gemini"
        else:
            name = "anthropic"

    if name == "stub":
        from time_travel.providers.stub_provider import StubProvider

        return StubProvider()
    if name == "anthropic":
        from time_travel.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    if name == "openai":
        from time_travel.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=os.environ.get("OPENAI_API_KEY", ""))
    if name == "gemini":
        from time_travel.providers.gemini_provider import GeminiProvider

        return GeminiProvider(api_key=os.environ.get("GEMINI_API_KEY", ""))
    raise ValueError(f"Unknown provider: {name}")


def _resolve_search(opts: RunOptions) -> WebSearch:
    if opts.search == "stub":
        from time_travel.search.stub_search import StubSearch

        return StubSearch()

    from time_travel.search.tavily import TavilySearch

    return TavilySearch(api_key=os.environ.get("TAVILY_API_KEY", ""))


async def _phase1_user_pov_and_blind_spots(
    provider: LLMProvider, plan_text: str
) -> tuple[UserPOV, list[BuriedRisk]]:
    prompt = (
        "Given this plan, return strict JSON with two keys: "
        '"user_pov" (object with thought_getting, would_forgive, untrustworthy, '
        'predictable_complaints) and "blind_spots" (array of objects with name, '
        f"why_unspoken, how_to_surface — risks nobody involved wants to name).\n\n"
        f"Plan:\n{plan_text}"
    )
    parsed = _try_json(await provider.complete(prompt))
    if not isinstance(parsed, dict):
        return UserPOV("", "", "", ""), []

    pov_raw = parsed.get("user_pov", parsed)
    pov_data = pov_raw if isinstance(pov_raw, dict) else {}
    user_pov = UserPOV(
        thought_getting=pov_data.get("thought_getting", ""),
        would_forgive=pov_data.get("would_forgive", ""),
        untrustworthy=pov_data.get("untrustworthy", ""),
        predictable_complaints=pov_data.get("predictable_complaints", ""),
    )
    blind_spots = [
        BuriedRisk(
            id=0,
            name=b.get("name", ""),
            why_unspoken=b.get("why_unspoken", ""),
            how_to_surface=b.get("how_to_surface", ""),
        )
        for b in parsed.get("blind_spots", [])
        if isinstance(b, dict)
    ]
    return user_pov, blind_spots


async def _phase2_evidence(
    search: WebSearch, personas: list[Persona], plan_title: str
) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    for persona in personas:
        results = await search.search(f"{persona.name} risk case study {plan_title}")
        for result in results[:1]:
            evidence.append(
                EvidenceItem(
                    title=result.title,
                    url=result.url,
                    when="",
                    who="",
                    what_happened=result.snippet,
                    why_relevant=f"Retrieved for the {persona.name} lens.",
                )
            )
    return evidence


def _persona_call(persona: Persona, plan_text: str) -> dict[str, str]:
    system = (
        f"You are the '{persona.name}' persona: {persona.pov} "
        f"You care about: {', '.join(persona.cares_about)}. "
        f"You tend to overlook: {', '.join(persona.overlooks)}."
    )
    prompt = (
        "Given this plan, return a strict JSON array of risk objects, each with: "
        "name, severity (object with technical, financial, trust, user_pain, "
        'ops_load, strategic — each 0-3), likelihood ("Low"|"Medium"|"High"), '
        "tripwire, change_my_mind, mitigation_summary, owner_shape, "
        f"citations (array of strings).\n\nPlan:\n{plan_text}"
    )
    return {"prompt": prompt, "system": system}


async def _phase3_persona_fanout(
    provider: LLMProvider, personas: list[Persona], plan_text: str
) -> list[PersonaRiskClaim]:
    calls = [_persona_call(p, plan_text) for p in personas]
    responses = await provider.complete_parallel(calls) if calls else []

    claims: list[PersonaRiskClaim] = []
    for persona, raw in zip(personas, responses):
        parsed = _try_json(raw)
        if not isinstance(parsed, list):
            continue
        for item in parsed:
            if not isinstance(item, dict):
                continue
            sev = item.get("severity") or {}
            claims.append(
                PersonaRiskClaim(
                    persona=persona.name,
                    name=item.get("name", ""),
                    severity=SeverityScore(
                        technical=sev.get("technical", 0),
                        financial=sev.get("financial", 0),
                        trust=sev.get("trust", 0),
                        user_pain=sev.get("user_pain", 0),
                        ops_load=sev.get("ops_load", 0),
                        strategic=sev.get("strategic", 0),
                    ),
                    likelihood=item.get("likelihood", "Medium"),
                    citations=item.get("citations", []),
                    tripwire=item.get("tripwire", ""),
                    change_my_mind=item.get("change_my_mind", ""),
                    mitigation_summary=item.get("mitigation_summary", ""),
                    owner_shape=item.get("owner_shape", ""),
                )
            )
    return claims


async def _phase3_5_rebuttal(provider: LLMProvider, claims: list[PersonaRiskClaim]) -> Rebuttal:
    if not claims:
        return Rebuttal([], [], [])
    names = sorted({c.name for c in claims if c.name})
    prompt = (
        "The personas raised these risks: "
        + "; ".join(names)
        + ". Return strict JSON with keys agreements, disagreements, cascades — "
        "each an array of short strings describing how the personas react to "
        "each other's risks."
    )
    parsed = _try_json(await provider.complete(prompt))
    if not isinstance(parsed, dict):
        return Rebuttal([], [], [])
    return Rebuttal(
        agreements=parsed.get("agreements", []),
        disagreements=parsed.get("disagreements", []),
        cascades=parsed.get("cascades", []),
    )


async def _phase4_revised_plan(
    provider: LLMProvider, plan_text: str, mitigations: list[Mitigation]
) -> str:
    if not mitigations:
        return plan_text
    actions = "; ".join(m.action for m in mitigations if m.action)
    if not actions:
        return plan_text
    prompt = f"Revise this plan to incorporate these mitigations: {actions}.\n\nPlan:\n{plan_text}"
    return await provider.complete(prompt)


async def run(
    source: str | None,
    opts: RunOptions,
    *,
    provider: LLMProvider | None = None,
    search: WebSearch | None = None,
) -> Report:
    provider = provider or _resolve_provider(opts)
    search = search or _resolve_search(opts)
    log: list[str] = []

    plan_title, plan_text = _ingest_plan(source)
    log.append(f"Phase 0: ingested plan '{plan_title}' ({len(plan_text)} chars)")

    user_pov, blind_spots = await _phase1_user_pov_and_blind_spots(provider, plan_text)
    log.append("Phase 1: user-POV + blind-spot candidates captured")

    personas = select_roster(plan_text, ai_source=opts.ai_source)
    evidence = await _phase2_evidence(search, personas, plan_title)
    log.append(f"Phase 2: selected {len(personas)} personas, {len(evidence)} evidence items")

    claims = await _phase3_persona_fanout(provider, personas, plan_text)
    log.append(f"Phase 3: {len(claims)} raw risk claims collected")

    rebuttal = await _phase3_5_rebuttal(provider, claims)
    log.append("Phase 3.5: rebuttal round complete")

    confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=blind_spots)
    mitigations = [
        Mitigation(risk_id=r.id, action=r.mitigation_summary, owner_shape=r.owner_shape, by="T+3mo")
        for r in confirmed
    ]
    mitigated_ids = {m.risk_id for m in mitigations}
    unmitigated_confidence, mitigated_confidence = compute_confidence(confirmed, mitigated_ids)
    revised_plan = await _phase4_revised_plan(provider, plan_text, mitigations)
    log.append(
        f"Phase 4: {len(confirmed)} confirmed, {len(inflated)} inflated, "
        f"{len(buried)} buried risks; confidence {unmitigated_confidence}->{mitigated_confidence}"
    )

    generated_at = datetime.now()
    report = Report(
        plan_title=plan_title,
        plan_source=source or "stdin",
        generated_at=generated_at,
        horizons=opts.horizons.split(","),
        plan_text=plan_text,
        user_pov=user_pov,
        personas=[PersonaActivation(name=p.name, rationale=p.pov) for p in personas],
        narratives={},
        confirmed_risks=confirmed,
        inflated_risks=inflated,
        buried_risks=buried,
        rebuttal=rebuttal,
        mitigations=mitigations,
        revised_plan=revised_plan,
        evidence=evidence,
        unmitigated_confidence=unmitigated_confidence,
        mitigated_confidence=mitigated_confidence,
        flags_used={"fast": opts.fast, "for_exec": opts.for_exec, "ai_source": opts.ai_source},
        ai_source=opts.ai_source,
        report_id=generated_at.strftime("%Y-%m-%dT%H%M%S"),
    )

    output_dir = Path(opts.output) / report.report_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report.json").write_text(
        report.to_json(), encoding="utf-8"  # type: ignore[attr-defined]
    )
    render_html_to_file(report, output_dir / "report.html")
    render_markdown_to_file(report, output_dir / "report.md")

    if opts.for_exec:
        exec_path = output_dir / "exec.md"
        render_exec_to_file(report, exec_path)
        report.exec_pager_path = str(exec_path)

    if not opts.no_process_log:
        log_path = output_dir / "process.log"
        log.append(f"Phase 5: artifacts written to {output_dir}")
        log_path.write_text("\n".join(log) + "\n", encoding="utf-8")
        report.process_log_path = str(log_path)

    return report


def render_from_json(report_json_path: str, output_dir: str) -> Path:
    """Re-render report.html/.md/exec.md from a saved Report JSON. No LLM calls."""
    data = Path(report_json_path).read_text(encoding="utf-8")
    report = Report.from_json(data)  # type: ignore[attr-defined]

    out = Path(output_dir) / (report.report_id or "rendered")
    out.mkdir(parents=True, exist_ok=True)
    render_html_to_file(report, out / "report.html")
    render_markdown_to_file(report, out / "report.md")
    if report.exec_pager_path:
        render_exec_to_file(report, out / "exec.md")
    return out
