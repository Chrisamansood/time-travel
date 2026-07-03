"""Tests for persona library and selection logic."""
from __future__ import annotations

from time_travel.personas.library import (
    CONDITIONAL_PERSONAS,
    DOMAIN_PERSONAS,
    PERSONAL_PERSONAS,
    PERSONAS,
    PERSONAS_BY_ID,
    PERSONAS_BY_NAME,
    UNIVERSAL_PERSONAS,
    Persona,
    PersonaCategory,
)
from time_travel.personas.selection import select_roster


def test_library_has_22_personas():
    assert len(PERSONAS) == 22


def test_library_ids_unique():
    ids = [p.id for p in PERSONAS]
    assert len(ids) == len(set(ids))


def test_library_names_unique():
    names = [p.name for p in PERSONAS]
    assert len(names) == len(set(names))


def test_library_all_have_required_fields():
    for p in PERSONAS:
        assert p.name
        assert p.pov
        assert len(p.cares_about) >= 1
        assert len(p.overlooks) >= 1
        assert p.first_line


def test_library_category_counts():
    assert len(UNIVERSAL_PERSONAS) == 3
    assert len(DOMAIN_PERSONAS) == 15
    assert len(PERSONAL_PERSONAS) == 3
    assert len(CONDITIONAL_PERSONAS) == 1


def test_lookup_by_name():
    p = PERSONAS_BY_NAME["Skeptical-Money"]
    assert p.id == 1
    assert p.category == PersonaCategory.UNIVERSAL


def test_lookup_by_id():
    p = PERSONAS_BY_ID[22]
    assert p.name == "AI-Optimism Auditor"
    assert p.category == PersonaCategory.CONDITIONAL


def test_select_roster_returns_5_to_7():
    plan = "We are building a SaaS product with billing, user onboarding, and ops infrastructure."
    roster = select_roster(plan)
    assert 5 <= len(roster) <= 7


def test_select_roster_includes_universals():
    plan = "Launch a product with billing and support."
    roster = select_roster(plan)
    names = {p.name for p in roster}
    universal_names = {p.name for p in UNIVERSAL_PERSONAS}
    assert len(names & universal_names) >= 2


def test_select_roster_no_duplicates():
    plan = "Finance budget ROI user ux adoption ops infrastructure data pipeline security auth."
    roster = select_roster(plan)
    ids = [p.id for p in roster]
    assert len(ids) == len(set(ids))


def test_select_roster_ai_source_includes_auditor():
    plan = "Build a product."
    roster = select_roster(plan, ai_source=True)
    names = {p.name for p in roster}
    assert "AI-Optimism Auditor" in names


def test_select_roster_detects_ai_patterns():
    plan = "This holistic and seamless solution will leverage synergy to achieve end-to-end transformation."
    roster = select_roster(plan)
    names = {p.name for p in roster}
    assert "AI-Optimism Auditor" in names


def test_select_roster_personal_plan():
    plan = "I want to change my career. I plan to learn Python and build my personal brand."
    roster = select_roster(plan)
    categories = {p.category for p in roster}
    assert PersonaCategory.PERSONAL in categories


def test_select_roster_respects_max():
    plan = "Finance budget ROI user ux adoption ops infrastructure data pipeline security auth sales revenue."
    roster = select_roster(plan, max_personas=5)
    assert len(roster) <= 5


def test_select_roster_always_returns_at_least_universals():
    plan = "xyzzy foobar bazzle."
    roster = select_roster(plan)
    assert len(roster) >= 3
