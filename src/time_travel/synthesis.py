"""Synthesis — dedupe, classify, and score raw persona risk claims.

Pure functions only: no I/O, no LLM calls. Consumes PersonaRiskClaim
(the parsed shape of a single persona's risk mention) and produces the
classified risk lists and confidence scores that populate a Report.

Family merging and classification port the semantics from the skill's
references/classification.md and references/synthesis.md (§1): fuzzy
name matching (not exact match) so claims like "Budget overrun" and
"Cost overrun" collapse into one family, with a mechanism check that
keeps claims separate when they fail for genuinely different reasons.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from time_travel.models import BuriedRisk, InflatedRisk, Risk, SeverityScore

_SEVERITY_MAX_PER_AXIS = 3
_SEVERITY_AXES = 6
_MAX_PENALTY_PER_RISK = 100 / 6  # so ~6 max-severity confirmed risks floor confidence at 0
_MITIGATION_LIFT_FRACTION = 0.5  # mitigating a risk recovers half its penalty

# Family-merging thresholds (documented per audit C1/C2 fix — see docs/handoff).
# Token-sort ratio via difflib stands in for rapidfuzz's token_sort_ratio: no
# extra dependency, same normalization idea (order-independent token overlap).
NAME_SIMILARITY_THRESHOLD = 0.6
MECHANISM_DIFFERENT_THRESHOLD = 0.25

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class PersonaRiskClaim:
    """One persona's raw mention of a risk, before dedupe/classification."""
    persona: str
    name: str
    severity: SeverityScore
    likelihood: str
    mechanism: str = ""
    citations: list[str] = field(default_factory=list)
    internal_signal: str = ""
    hedged_language: bool = False
    tripwire: str = ""
    change_my_mind: str = ""
    mitigation_summary: str = ""
    owner_shape: str = ""


def _token_sort_ratio(a: str, b: str) -> float:
    """Order-independent similarity ratio on normalized tokens, 0.0-1.0."""
    tokens_a = sorted(_TOKEN_RE.findall(a.lower()))
    tokens_b = sorted(_TOKEN_RE.findall(b.lower()))
    if not tokens_a and not tokens_b:
        return 1.0
    return difflib.SequenceMatcher(None, " ".join(tokens_a), " ".join(tokens_b)).ratio()


def _mechanisms_clearly_different(mechanism_a: str, mechanism_b: str) -> bool:
    """True only when both mechanisms are stated and diverge sharply.

    An empty mechanism means "unknown" — we don't split families on
    missing data, only on evidence that the failure paths differ.
    """
    if not mechanism_a.strip() or not mechanism_b.strip():
        return False
    return _token_sort_ratio(mechanism_a, mechanism_b) < MECHANISM_DIFFERENT_THRESHOLD


@dataclass
class _Family:
    canonical_name: str
    canonical_mechanism: str
    claims: list[PersonaRiskClaim] = field(default_factory=list)


def _build_families(claims: list[PersonaRiskClaim]) -> list[_Family]:
    """Group claims into failure-mode families by fuzzy name + mechanism.

    Greedy, order-preserving: each claim joins the first existing family
    whose canonical name is similar enough AND whose mechanism isn't
    clearly different, else it starts a new family. Deterministic given
    stable input order (per synthesis.md §1: keep separate if mechanisms
    differ, even when names match).
    """
    families: list[_Family] = []
    for claim in claims:
        target: _Family | None = None
        for family in families:
            if _token_sort_ratio(claim.name, family.canonical_name) < NAME_SIMILARITY_THRESHOLD:
                continue
            if _mechanisms_clearly_different(claim.mechanism, family.canonical_mechanism):
                continue
            target = family
            break
        if target is None:
            families.append(_Family(canonical_name=claim.name, canonical_mechanism=claim.mechanism))
            target = families[-1]
        target.claims.append(claim)
    return families


def _severity_total(severity: SeverityScore) -> int:
    return (
        severity.technical
        + severity.financial
        + severity.trust
        + severity.user_pain
        + severity.ops_load
        + severity.strategic
    )


def _merge_severity(a: SeverityScore, b: SeverityScore) -> SeverityScore:
    return SeverityScore(
        technical=max(a.technical, b.technical),
        financial=max(a.financial, b.financial),
        trust=max(a.trust, b.trust),
        user_pain=max(a.user_pain, b.user_pain),
        ops_load=max(a.ops_load, b.ops_load),
        strategic=max(a.strategic, b.strategic),
    )


def _urgency_from_severity(severity: SeverityScore) -> str:
    total = _severity_total(severity)
    if total >= 12:
        return "Block"
    if total >= 6:
        return "Patch-fast"
    return "Monitor"


def _earliest_tripwire(group: list[PersonaRiskClaim]) -> str:
    """First non-empty tripwire in family order — a deterministic proxy for
    "earliest-firing" (true temporal ordering needs judgment the engine
    can't derive from text; documented as a judgment call)."""
    for claim in group:
        if claim.tripwire.strip():
            return claim.tripwire
    return ""


def _most_specific_change_my_mind(group: list[PersonaRiskClaim]) -> str:
    """Longest non-empty answer in the family — a deterministic proxy for
    "most specific" (documented as a judgment call, same rationale as
    _earliest_tripwire)."""
    candidates = [c.change_my_mind for c in group if c.change_my_mind.strip()]
    return max(candidates, key=len) if candidates else ""


def classify_risks(
    claims: list[PersonaRiskClaim],
    blind_spot_candidates: list[BuriedRisk],
) -> tuple[list[Risk], list[InflatedRisk], list[BuriedRisk]]:
    """Fuzzy-merge persona claims into families, then classify each family.

    Confirmed requires (per classification.md): a citation to evidence,
    OR a non-empty internal_signal, OR cross-persona agreement within the
    fuzzy-merged family. "Specific formulation" and "observable tripwire"
    are Phase-3 authoring concerns enforced by the skill's prompt, not
    re-derivable from text here — the engine trusts claims that reach it
    were phrased specifically (documented judgment call).

    Families that don't qualify as Confirmed but contain a hedged_language
    claim go to Buried (politically-avoided, not evidence-poor); everything
    else falls to Inflated with a one-line why-downgraded note.
    """
    families = _build_families(claims)

    confirmed: list[Risk] = []
    inflated: list[InflatedRisk] = []
    hedged_buried: list[BuriedRisk] = []
    next_confirmed_id = 1
    next_inflated_id = 1

    for family in families:
        group = family.claims
        personas = {c.persona for c in group}
        citations = sorted({cite for c in group for cite in c.citations})
        internal_signals = [c.internal_signal for c in group if c.internal_signal.strip()]
        cross_persona_agreement = len(personas) >= 2
        is_confirmed = bool(citations) or bool(internal_signals) or cross_persona_agreement

        if is_confirmed:
            severity = group[0].severity
            for claim in group[1:]:
                severity = _merge_severity(severity, claim.severity)
            confirmed.append(
                Risk(
                    id=next_confirmed_id,
                    name=family.canonical_name,
                    severity=severity,
                    likelihood=group[0].likelihood,
                    urgency=_urgency_from_severity(severity),
                    tripwire=_earliest_tripwire(group),
                    change_my_mind=_most_specific_change_my_mind(group),
                    mitigation_summary=group[0].mitigation_summary,
                    owner_shape=group[0].owner_shape,
                    citations=citations,
                )
            )
            next_confirmed_id += 1
            continue

        if any(c.hedged_language for c in group):
            hedged_buried.append(
                BuriedRisk(
                    id=0,
                    name=family.canonical_name,
                    why_unspoken=(
                        "Raised only in hedged, indirect language — no citation, internal "
                        "signal, or corroborating persona to state it plainly."
                    ),
                    how_to_surface=(
                        f"Ask directly: what would it take to state "
                        f"'{family.canonical_name}' plainly?"
                    ),
                )
            )
            continue

        inflated.append(
            InflatedRisk(
                id=next_inflated_id,
                name=family.canonical_name,
                why_downgraded=(
                    "Raised by only one persona with no supporting evidence."
                    if not cross_persona_agreement
                    else "Agreed on by multiple personas but no supporting evidence found."
                ),
            )
        )
        next_inflated_id += 1

    raised_names = [family.canonical_name for family in families]
    buried: list[BuriedRisk] = list(hedged_buried)
    for candidate in blind_spot_candidates:
        already_raised = any(
            _token_sort_ratio(candidate.name, raised) >= NAME_SIMILARITY_THRESHOLD
            for raised in raised_names
        )
        if already_raised:
            continue
        buried.append(
            BuriedRisk(
                id=0,
                name=candidate.name,
                why_unspoken=candidate.why_unspoken,
                how_to_surface=candidate.how_to_surface,
            )
        )

    for i, risk in enumerate(buried, start=1):
        risk.id = i

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


# Confidence bands (audit C4): the 0-100 math is heuristic and uncalibrated
# against any real premortem, so rendered output shows a qualitative band
# instead of a raw percentage. Thresholds are the upper bound (exclusive)
# of each band below "High".
_CONFIDENCE_BAND_THRESHOLDS: tuple[tuple[int, str], ...] = (
    (40, "Low"),
    (60, "Guarded"),
    (80, "Moderate"),
)


def confidence_band(score: int) -> str:
    """Map a 0-100 confidence score to a qualitative band."""
    for threshold, label in _CONFIDENCE_BAND_THRESHOLDS:
        if score < threshold:
            return label
    return "High"


def confidence_drivers(confirmed_risks: list[Risk]) -> str:
    """One-line explanation of what's behind a confidence band."""
    block_count = sum(1 for r in confirmed_risks if r.urgency == "Block")
    risk_word = "risk" if len(confirmed_risks) == 1 else "risks"
    return f"driven by: {len(confirmed_risks)} confirmed {risk_word}, {block_count} at Block tier"


def confidence_render_context(
    unmitigated_confidence: int, mitigated_confidence: int, confirmed_risks: list[Risk]
) -> dict[str, str]:
    """Template context shared by every renderer (html/md/exec) — bands and
    drivers, never the raw uncalibrated percentages (audit C4)."""
    return {
        "unmitigated_band": confidence_band(unmitigated_confidence),
        "mitigated_band": confidence_band(mitigated_confidence),
        "confidence_drivers": confidence_drivers(confirmed_risks),
    }
