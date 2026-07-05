"""Unit tests for synthesis.py — fuzzy dedupe, classification, confidence math.

Pure-function module: no I/O, no LLM calls. Inputs are hand-built
PersonaRiskClaim / BuriedRisk fixtures standing in for what the claims
JSON (schema v1) parses into.
"""
from __future__ import annotations

from time_travel.models import BuriedRisk, SeverityScore
from time_travel.synthesis import PersonaRiskClaim, classify_risks, compute_confidence


def _claim(
    persona: str,
    name: str,
    *,
    mechanism: str = "",
    severity: SeverityScore | None = None,
    likelihood: str = "Medium",
    citations: list[str] | None = None,
    internal_signal: str = "",
    hedged_language: bool = False,
    tripwire: str = "some early signal",
    change_my_mind: str = "some counter-evidence",
    mitigation_summary: str = "do the obvious thing",
    owner_shape: str = "Eng lead",
) -> PersonaRiskClaim:
    return PersonaRiskClaim(
        persona=persona,
        name=name,
        mechanism=mechanism,
        severity=severity or SeverityScore(),
        likelihood=likelihood,
        citations=citations or [],
        internal_signal=internal_signal,
        hedged_language=hedged_language,
        tripwire=tripwire,
        change_my_mind=change_my_mind,
        mitigation_summary=mitigation_summary,
        owner_shape=owner_shape,
    )


class TestFuzzyDedupe:
    """Gate for audit C1/C2: family merging must be fuzzy, not exact-name."""

    def test_similar_names_with_similar_mechanism_merge_into_one_family(self):
        claims = [
            _claim(
                "Skeptical-Money",
                "Budget overrun",
                mechanism="Vendor costs exceed the fixed-price contract ceiling",
            ),
            _claim(
                "Frustrated-End-User",
                "Cost overrun",
                mechanism="Vendor costs exceed the fixed-price contract ceiling",
            ),
        ]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 1
        assert len(inflated) == 0
        assert confirmed[0].name == "Budget overrun"

    def test_same_name_but_clearly_different_mechanisms_stay_separate(self):
        claims = [
            _claim(
                "Skeptical-Money",
                "Budget overrun",
                mechanism="Vendor SLA gap forces an expensive emergency contract",
                citations=["case-a"],
            ),
            _claim(
                "Ops-Engineer",
                "Budget overrun",
                mechanism="Internal team lacks headcount to deliver on schedule",
                citations=["case-b"],
            ),
        ]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 2
        assert {r.name for r in confirmed} == {"Budget overrun"}
        assert confirmed[0].citations == ["case-a"]
        assert confirmed[1].citations == ["case-b"]

    def test_case_insensitive_names_merge(self):
        claims = [
            _claim("Skeptical-Money", "Budget Overrun"),
            _claim("Frustrated-End-User", "budget overrun"),
        ]

        confirmed, _, _ = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 1

    def test_merged_risk_unions_citations_from_all_personas(self):
        claims = [
            _claim("Skeptical-Money", "Budget overrun", citations=["case-a"]),
            _claim("Frustrated-End-User", "Budget overrun", citations=["case-b"]),
        ]

        confirmed, _, _ = classify_risks(claims, blind_spot_candidates=[])

        assert set(confirmed[0].citations) == {"case-a", "case-b"}

    def test_unrelated_names_do_not_merge(self):
        claims = [
            _claim("Skeptical-Money", "Budget overrun", citations=["case-a"]),
            _claim("Frustrated-End-User", "Support team burnout", citations=["case-b"]),
        ]

        confirmed, _, _ = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 2


class TestClassification:
    def test_citation_alone_from_single_persona_is_confirmed(self):
        claims = [_claim("Skeptical-Money", "Lone claim", citations=["case-a"])]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 1
        assert len(inflated) == 0

    def test_internal_signal_alone_from_single_persona_is_confirmed(self):
        claims = [
            _claim(
                "Skeptical-Money",
                "Undefined vendor roadmap",
                internal_signal="Plan depends on a vendor feature with no committed ship date",
            )
        ]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 1
        assert len(inflated) == 0

    def test_cross_persona_agreement_alone_is_confirmed(self):
        claims = [
            _claim("Skeptical-Money", "Budget overrun"),
            _claim("Frustrated-End-User", "Budget overrun"),
        ]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 1
        assert len(inflated) == 0

    def test_single_persona_no_citation_no_signal_is_inflated(self):
        claims = [_claim("Skeptical-Money", "Vague fear")]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 0
        assert len(inflated) == 1
        assert inflated[0].name == "Vague fear"

    def test_hedged_language_without_evidence_is_buried_not_inflated(self):
        claims = [
            _claim(
                "Skeptical-Money",
                "Leadership alignment concern",
                hedged_language=True,
            )
        ]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 0
        assert len(inflated) == 0
        assert len(buried) == 1
        assert buried[0].name == "Leadership alignment concern"

    def test_hedged_language_with_citation_is_still_confirmed(self):
        claims = [
            _claim(
                "Skeptical-Money",
                "Leadership alignment concern",
                hedged_language=True,
                citations=["case-a"],
            )
        ]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=[])

        assert len(confirmed) == 1
        assert len(buried) == 0

    def test_confirmed_risks_get_sequential_ids_starting_at_one(self):
        claims = [
            _claim("A", "Risk one", citations=["c1"]),
            _claim("B", "Risk one", citations=["c2"]),
            _claim("A", "Risk two entirely unrelated topic", citations=["c3"]),
            _claim("B", "Risk two entirely unrelated topic", citations=["c4"]),
        ]

        confirmed, _, _ = classify_risks(claims, blind_spot_candidates=[])

        assert sorted(r.id for r in confirmed) == [1, 2]

    def test_blind_spot_not_raised_by_any_persona_is_buried(self):
        blind_spots = [
            BuriedRisk(
                id=0,
                name="Nobody owns the migration rollback",
                why_unspoken="Politically awkward to admit",
                how_to_surface="Ask directly in the retro",
            )
        ]

        confirmed, inflated, buried = classify_risks([], blind_spot_candidates=blind_spots)

        assert len(buried) == 1
        assert buried[0].name == "Nobody owns the migration rollback"

    def test_blind_spot_fuzzy_matched_to_a_raised_claim_is_not_buried(self):
        claims = [_claim("Skeptical-Money", "Migration rollback plan", citations=["case-a"])]
        blind_spots = [
            BuriedRisk(
                id=0,
                name="Migration rollback",
                why_unspoken="n/a",
                how_to_surface="n/a",
            )
        ]

        confirmed, inflated, buried = classify_risks(claims, blind_spot_candidates=blind_spots)

        assert len(buried) == 0

    def test_buried_risks_get_sequential_ids_starting_at_one(self):
        blind_spots = [
            BuriedRisk(
                id=0, name="A completely unrelated topic one", why_unspoken="x", how_to_surface="y"
            ),
            BuriedRisk(
                id=0, name="A completely unrelated topic two", why_unspoken="x", how_to_surface="y"
            ),
        ]

        _, _, buried = classify_risks([], blind_spot_candidates=blind_spots)

        assert sorted(r.id for r in buried) == [1, 2]

    def test_no_claims_and_no_blind_spots_returns_empty_lists(self):
        confirmed, inflated, buried = classify_risks([], blind_spot_candidates=[])

        assert confirmed == []
        assert inflated == []
        assert buried == []


class TestFamilyMerging:
    def test_severity_merges_by_per_lens_max(self):
        claims = [
            _claim(
                "A",
                "Budget overrun",
                severity=SeverityScore(
                    technical=1, financial=3, trust=0, user_pain=0, ops_load=0, strategic=0
                ),
            ),
            _claim(
                "B",
                "Budget overrun",
                severity=SeverityScore(
                    technical=2, financial=1, trust=0, user_pain=0, ops_load=0, strategic=0
                ),
            ),
        ]

        confirmed, _, _ = classify_risks(claims, blind_spot_candidates=[])

        assert confirmed[0].severity.technical == 2
        assert confirmed[0].severity.financial == 3

    def test_tripwire_takes_earliest_non_empty_in_family_order(self):
        claims = [
            _claim("A", "Budget overrun", tripwire=""),
            _claim("B", "Budget overrun", tripwire="burn rate exceeds plan in week 3"),
        ]

        confirmed, _, _ = classify_risks(claims, blind_spot_candidates=[])

        assert confirmed[0].tripwire == "burn rate exceeds plan in week 3"

    def test_change_my_mind_takes_most_specific_in_family(self):
        claims = [
            _claim("A", "Budget overrun", change_my_mind="a signed vendor discount"),
            _claim(
                "B",
                "Budget overrun",
                change_my_mind=(
                    "a signed vendor discount amendment reducing the per-seat rate by 20%"
                ),
            ),
        ]

        confirmed, _, _ = classify_risks(claims, blind_spot_candidates=[])

        assert confirmed[0].change_my_mind == (
            "a signed vendor discount amendment reducing the per-seat rate by 20%"
        )


class TestConfidenceMath:
    def test_no_confirmed_risks_gives_full_confidence(self):
        unmitigated, mitigated = compute_confidence(confirmed_risks=[], mitigated_risk_ids=set())

        assert unmitigated == 100
        assert mitigated == 100

    def test_each_confirmed_risk_lowers_unmitigated_confidence(self):
        low_severity = SeverityScore(
            technical=0, financial=0, trust=1, user_pain=1, ops_load=0, strategic=0
        )
        risks = [
            _risk(1, "Risk A", low_severity),
            _risk(2, "Risk B", low_severity),
        ]

        unmitigated_one, _ = compute_confidence(
            confirmed_risks=risks[:1], mitigated_risk_ids=set()
        )
        unmitigated_two, _ = compute_confidence(confirmed_risks=risks, mitigated_risk_ids=set())

        assert unmitigated_two < unmitigated_one

    def test_higher_severity_lowers_confidence_more(self):
        low = SeverityScore(
            technical=0, financial=0, trust=1, user_pain=0, ops_load=0, strategic=0
        )
        high = SeverityScore(
            technical=3, financial=3, trust=3, user_pain=3, ops_load=3, strategic=3
        )

        unmitigated_low, _ = compute_confidence(
            confirmed_risks=[_risk(1, "Low", low)], mitigated_risk_ids=set()
        )
        unmitigated_high, _ = compute_confidence(
            confirmed_risks=[_risk(1, "High", high)], mitigated_risk_ids=set()
        )

        assert unmitigated_high < unmitigated_low

    def test_mitigating_a_risk_raises_confidence_above_unmitigated(self):
        severity = SeverityScore(
            technical=0, financial=0, trust=2, user_pain=2, ops_load=0, strategic=0
        )
        risk = _risk(1, "Risk A", severity)

        unmitigated, mitigated_none = compute_confidence(
            confirmed_risks=[risk], mitigated_risk_ids=set()
        )
        _, mitigated_all = compute_confidence(confirmed_risks=[risk], mitigated_risk_ids={1})

        assert mitigated_none == unmitigated
        assert mitigated_all > unmitigated

    def test_confidence_never_exceeds_100_or_drops_below_0(self):
        max_severity = SeverityScore(
            technical=3, financial=3, trust=3, user_pain=3, ops_load=3, strategic=3
        )
        many_risks = [_risk(i, f"Risk {i}", max_severity) for i in range(1, 30)]

        unmitigated, mitigated = compute_confidence(
            confirmed_risks=many_risks, mitigated_risk_ids={r.id for r in many_risks}
        )

        assert 0 <= unmitigated <= 100
        assert 0 <= mitigated <= 100


def _risk(id_: int, name: str, severity: SeverityScore):
    from time_travel.models import Risk

    return Risk(
        id=id_,
        name=name,
        severity=severity,
        likelihood="Medium",
        urgency="Monitor",
        tripwire="signal",
        change_my_mind="evidence",
        mitigation_summary="action",
        owner_shape="Eng lead",
    )
