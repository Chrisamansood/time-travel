"""Synthesis — dedupe, classify, and score raw persona risk claims.

Pure functions only: no I/O, no LLM calls. Consumes PersonaRiskClaim
(the parsed shape of a single persona's risk mention) and produces the
classified risk lists and confidence scores that populate a Report.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from time_travel.models import BuriedRisk, InflatedRisk, Risk, SeverityScore

_SEVERITY_MAX_PER_AXIS = 3
_SEVERITY_AXES = 6
_MAX_PENALTY_PER_RISK = 100 / 6  # so ~6 max-severity confirmed risks floor confidence at 0
_MITIGATION_LIFT_FRACTION = 0.5  # mitigating a risk recovers half its penalty


@dataclass
class PersonaRiskClaim:
    """One persona's raw mention of a risk, before dedupe/classification."""
    persona: str
    name: str
    severity: SeverityScore
    likelihood: str
    citations: list[str] = field(default_factory=list)
    tripwire: str = ""
    change_my_mind: str = ""
    mitigation_summary: str = ""
    owner_shape: str = ""


def _severity_total(severity: SeverityScore) -> int:
    return (
        severity.trust
        + severity.user_pain
        + severity.blind_spot
        + severity.ops_load
        + severity.financial
        + severity.strategic
    )


def _merge_severity(a: SeverityScore, b: SeverityScore) -> SeverityScore:
    return SeverityScore(
        trust=max(a.trust, b.trust),
        user_pain=max(a.user_pain, b.user_pain),
        blind_spot=max(a.blind_spot, b.blind_spot),
        ops_load=max(a.ops_load, b.ops_load),
        financial=max(a.financial, b.financial),
        strategic=max(a.strategic, b.strategic),
    )


def _urgency_from_severity(severity: SeverityScore) -> str:
    total = _severity_total(severity)
    if total >= 12:
        return "Block"
    if total >= 6:
        return "Patch-fast"
    return "Monitor"


def classify_risks(
    claims: list[PersonaRiskClaim],
    blind_spot_candidates: list[BuriedRisk],
) -> tuple[list[Risk], list[InflatedRisk], list[BuriedRisk]]:
    """Dedupe persona claims by name, then classify Confirmed / Inflated / Buried."""
    grouped: dict[str, list[PersonaRiskClaim]] = {}
    for claim in claims:
        key = claim.name.strip().lower()
        grouped.setdefault(key, []).append(claim)

    confirmed: list[Risk] = []
    inflated: list[InflatedRisk] = []
    next_confirmed_id = 1
    next_inflated_id = 1

    for group in grouped.values():
        personas = {c.persona for c in group}
        citations = sorted({cite for c in group for cite in c.citations})
        has_evidence = bool(citations)
        agreed = len(personas) >= 2

        if agreed and has_evidence:
            severity = group[0].severity
            for claim in group[1:]:
                severity = _merge_severity(severity, claim.severity)
            confirmed.append(
                Risk(
                    id=next_confirmed_id,
                    name=group[0].name,
                    severity=severity,
                    likelihood=group[0].likelihood,
                    urgency=_urgency_from_severity(severity),
                    tripwire=group[0].tripwire,
                    change_my_mind=group[0].change_my_mind,
                    mitigation_summary=group[0].mitigation_summary,
                    owner_shape=group[0].owner_shape,
                    citations=citations,
                )
            )
            next_confirmed_id += 1
        else:
            inflated.append(
                InflatedRisk(
                    id=next_inflated_id,
                    name=group[0].name,
                    why_downgraded=(
                        "Raised by only one persona with no supporting evidence."
                        if not agreed
                        else "Agreed on by multiple personas but no supporting evidence found."
                    ),
                )
            )
            next_inflated_id += 1

    raised_names = {c.name.strip().lower() for c in claims}
    buried: list[BuriedRisk] = []
    for i, candidate in enumerate(blind_spot_candidates, start=1):
        if candidate.name.strip().lower() in raised_names:
            continue
        buried.append(
            BuriedRisk(
                id=i,
                name=candidate.name,
                why_unspoken=candidate.why_unspoken,
                how_to_surface=candidate.how_to_surface,
            )
        )

    return confirmed, inflated, buried


def compute_confidence(
    confirmed_risks: list[Risk],
    mitigated_risk_ids: set[int],
) -> tuple[int, int]:
    """Return (unmitigated_confidence, mitigated_confidence), each 0-100."""
    unmitigated = 100.0
    mitigated = 100.0

    max_severity = _SEVERITY_MAX_PER_AXIS * _SEVERITY_AXES
    for risk in confirmed_risks:
        severity_fraction = _severity_total(risk.severity) / max_severity
        penalty = severity_fraction * _MAX_PENALTY_PER_RISK
        unmitigated -= penalty
        if risk.id in mitigated_risk_ids:
            mitigated -= penalty * (1 - _MITIGATION_LIFT_FRACTION)
        else:
            mitigated -= penalty

    unmitigated = max(0, min(100, round(unmitigated)))
    mitigated = max(0, min(100, round(mitigated)))
    return unmitigated, mitigated
