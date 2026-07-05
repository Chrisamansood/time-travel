"""Claims-file ingestion — the interface between the LLM-driven skill and
the deterministic engine (audit resolved architecture, docs/handoff/).

The skill (Claude) does the thinking in-session and emits a claims JSON
file conforming to schemas/claims-v1.json. This module validates that
file and converts it into the shapes synthesis.py and models.Report
expect. Validation fails loud (audit C3): a malformed or degraded
claims file raises ClaimsValidationError naming exactly what's wrong,
rather than silently producing an empty or hollow report.
"""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any

import jsonschema

from time_travel.models import (
    BuriedRisk,
    EvidenceItem,
    PersonaActivation,
    Rebuttal,
    SeverityScore,
    UserPOV,
)
from time_travel.synthesis import PersonaRiskClaim

_SCHEMA_PACKAGE = "time_travel"
_SCHEMA_SUBDIR = "schemas"
_SCHEMA_FILENAME = "claims-v1.json"
_SEVERITY_AXES = ("technical", "financial", "trust", "user_pain", "ops_load", "strategic")

MIN_CLAIMS = 5
MIN_PERSONAS = 1


class ClaimsValidationError(ValueError):
    """Raised when a claims file fails validation. Message names what failed."""


def _load_schema() -> dict[str, Any]:
    schema_path = resources.files(_SCHEMA_PACKAGE).joinpath(_SCHEMA_SUBDIR).joinpath(
        _SCHEMA_FILENAME
    )
    schema_text = schema_path.read_text(encoding="utf-8")
    schema: dict[str, Any] = json.loads(schema_text)
    return schema


def _severity_is_all_zero(severity: dict[str, Any]) -> bool:
    return all(severity.get(axis, 0) == 0 for axis in _SEVERITY_AXES)


def load_claims_file(path: str | Path) -> dict[str, Any]:
    """Read, parse, and validate a claims JSON file. Raises loudly on any defect."""
    file_path = Path(path)
    if not file_path.is_file():
        raise ClaimsValidationError(f"Claims file not found: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ClaimsValidationError(
            f"Claims file is not valid JSON ({file_path}): {exc.msg} at line {exc.lineno}, "
            f"column {exc.colno}"
        ) from exc

    if not isinstance(data, dict):
        raise ClaimsValidationError(
            f"Claims file must contain a JSON object at the top level, got {type(data).__name__}"
        )

    # Check the common degraded-input cases first for a friendly, specific
    # message before falling through to full schema validation's detail dump.
    claims = data.get("claims", [])
    if isinstance(claims, list) and len(claims) < MIN_CLAIMS:
        raise ClaimsValidationError(
            f"Claims file has {len(claims)} claim(s); at least {MIN_CLAIMS} are required "
            "to synthesize a report"
        )

    personas = data.get("personas", [])
    if isinstance(personas, list) and len(personas) < MIN_PERSONAS:
        raise ClaimsValidationError(
            f"Claims file has {len(personas)} persona(s); at least {MIN_PERSONAS} is required"
        )

    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    schema_errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if schema_errors:
        details = "; ".join(
            f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
            for e in schema_errors[:5]
        )
        raise ClaimsValidationError(f"Claims file failed schema validation: {details}")

    if isinstance(claims, list) and all(
        _severity_is_all_zero(c.get("severity", {})) for c in claims
    ):
        raise ClaimsValidationError(
            "Every claim has all-zero severity across all six lenses — refusing to render "
            "a report with no risk signal"
        )

    return data


def _severity_from_dict(severity: dict[str, Any]) -> SeverityScore:
    return SeverityScore(**{axis: severity.get(axis, 0) for axis in _SEVERITY_AXES})


def claims_to_persona_risk_claims(data: dict[str, Any]) -> list[PersonaRiskClaim]:
    persona_names = {p["id"]: p["name"] for p in data.get("personas", [])}
    result: list[PersonaRiskClaim] = []
    for c in data["claims"]:
        persona_id = c.get("persona_id", "")
        result.append(
            PersonaRiskClaim(
                persona=persona_names.get(persona_id, persona_id),
                name=c["name"],
                mechanism=c.get("mechanism", ""),
                severity=_severity_from_dict(c.get("severity", {})),
                likelihood=c.get("likelihood", "medium").capitalize(),
                citations=list(c.get("citations", [])),
                internal_signal=c.get("internal_signal", ""),
                hedged_language=bool(c.get("hedged_language", False)),
                tripwire=c.get("tripwire", ""),
                change_my_mind=c.get("change_my_mind", ""),
                mitigation_summary=c.get("mitigation", ""),
                owner_shape=c.get("owner_shape", ""),
            )
        )
    return result


def claims_to_blind_spots(data: dict[str, Any]) -> list[BuriedRisk]:
    return [
        BuriedRisk(
            id=0,
            name=name,
            why_unspoken="Named as a politically-unspoken candidate during the user-POV pass.",
            how_to_surface=f"Ask directly: why hasn't '{name}' been named plainly in the plan?",
        )
        for name in data.get("blind_spot_candidates", [])
    ]


def claims_to_user_pov(data: dict[str, Any]) -> UserPOV:
    pov = data.get("user_pov", {})
    return UserPOV(
        thought_getting=pov.get("expectations", ""),
        would_forgive=pov.get("forgivable", ""),
        untrustworthy=pov.get("trust_breakers", ""),
        predictable_complaints=pov.get("predictable_complaints", ""),
    )


def claims_to_personas(data: dict[str, Any]) -> list[PersonaActivation]:
    return [
        PersonaActivation(name=p["name"], rationale=p.get("pov", ""))
        for p in data.get("personas", [])
    ]


def claims_to_evidence(data: dict[str, Any]) -> list[EvidenceItem]:
    return [
        EvidenceItem(
            title=e.get("title", ""),
            url=e.get("url", ""),
            when=e.get("when", ""),
            who=e.get("who", ""),
            what_happened=e.get("what_happened", ""),
            why_relevant=e.get("why_relevant", ""),
        )
        for e in data.get("evidence", [])
    ]


def claims_to_rebuttal(data: dict[str, Any]) -> Rebuttal:
    agreements: list[str] = []
    disagreements: list[str] = []
    cascades: list[str] = []
    for r in data.get("rebuttals", []):
        text = r.get("text", "")
        stance = r.get("stance")
        if stance == "agree":
            agreements.append(text)
        elif stance == "disagree":
            disagreements.append(text)
        elif stance == "cascade":
            cascades.append(text)
    return Rebuttal(agreements=agreements, disagreements=disagreements, cascades=cascades)
