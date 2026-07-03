"""Roster picker — select 5–7 personas for a given plan."""
from __future__ import annotations

from time_travel.personas.library import (
    DOMAIN_PERSONAS,
    PERSONAL_PERSONAS,
    UNIVERSAL_PERSONAS,
    Persona,
    PersonaCategory,
    PERSONAS_BY_NAME,
)


def select_roster(
    plan_text: str,
    ai_source: bool = False,
    max_personas: int = 7,
) -> list[Persona]:
    """Pick 2–3 universal + 3–4 domain-specific personas based on plan text.

    Uses keyword matching on domain_tags to score relevance.
    If ai_source is True or AI patterns are detected, the AI-Optimism Auditor is included.
    """
    plan_lower = plan_text.lower()

    universals = _pick_universals(plan_lower)

    is_personal = _detect_personal_plan(plan_lower)
    if is_personal:
        domain_pool = PERSONAL_PERSONAS
    else:
        domain_pool = DOMAIN_PERSONAS

    scored = []
    for persona in domain_pool:
        score = sum(1 for tag in persona.domain_tags if tag in plan_lower)
        scored.append((score, persona))

    scored.sort(key=lambda x: x[0], reverse=True)

    domain_budget = max_personas - len(universals)
    if ai_source or _detect_ai_patterns(plan_lower):
        ai_auditor = PERSONAS_BY_NAME.get("AI-Optimism Auditor")
        if ai_auditor:
            domain_budget -= 1

    domains = [p for _, p in scored[:domain_budget] if _ > 0]

    if len(domains) < 3 and len(scored) >= 3:
        domains = [p for _, p in scored[:3]]

    roster = universals + domains

    if ai_source or _detect_ai_patterns(plan_lower):
        ai_auditor = PERSONAS_BY_NAME.get("AI-Optimism Auditor")
        if ai_auditor and ai_auditor not in roster:
            roster.append(ai_auditor)

    seen = set()
    deduped = []
    for p in roster:
        if p.id not in seen:
            seen.add(p.id)
            deduped.append(p)

    return deduped[:max_personas]


def _pick_universals(plan_lower: str) -> list[Persona]:
    """Always include 2–3 universal personas."""
    result = []
    for persona in UNIVERSAL_PERSONAS:
        score = sum(1 for tag in persona.domain_tags if tag in plan_lower)
        result.append((score, persona))
    result.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in result[:3]]


def _detect_personal_plan(plan_lower: str) -> bool:
    personal_signals = ["my ", "i want", "i plan", "myself", "my career", "my life", "personal"]
    return sum(1 for s in personal_signals if s in plan_lower) >= 2


_AI_PATTERNS = [
    "leverage", "synergy", "seamless", "holistic", "robust", "end-to-end",
    "transformational", "best-in-class", "significant", "stakeholders",
    "40%", "10x", "90%", "save millions",
]


def _detect_ai_patterns(plan_lower: str) -> bool:
    hits = sum(1 for p in _AI_PATTERNS if p in plan_lower)
    return hits >= 3
