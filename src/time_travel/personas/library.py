"""Persona library — all 22 personas as dataclasses.

Converted from harnesses/claude-code/plugins/time-travel/skills/time-travel/references/persona-library.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PersonaCategory(str, Enum):
    UNIVERSAL = "universal"
    DOMAIN = "domain"
    PERSONAL = "personal"
    CONDITIONAL = "conditional"


@dataclass(frozen=True)
class Persona:
    id: int
    name: str
    category: PersonaCategory
    pov: str
    cares_about: list[str]
    overlooks: list[str]
    first_line: str
    domain_tags: list[str] = field(default_factory=list)
    condition: str | None = None


PERSONAS: list[Persona] = [
    Persona(
        id=1,
        name="Skeptical-Money",
        category=PersonaCategory.UNIVERSAL,
        pov="Whoever signs the cheque or has to defend the spend.",
        cares_about=["Unit economics", "Sunk cost", "Opportunity cost", "Hidden ongoing costs"],
        overlooks=["User joy", "Technical elegance", "Strategic narrative"],
        first_line="Walk me through what we get back, and when.",
        domain_tags=["finance", "budget", "roi"],
    ),
    Persona(
        id=2,
        name="Frustrated-End-User",
        category=PersonaCategory.UNIVERSAL,
        pov="The person who actually has to use the thing every day.",
        cares_about=["Friction", "Workarounds", "What breaks when", "Whether their input was ignored"],
        overlooks=["Strategic context", "Vendor relationships", "Executive constraints"],
        first_line="Did anyone ask us?",
        domain_tags=["ux", "user", "adoption"],
    ),
    Persona(
        id=3,
        name="Change-Resister",
        category=PersonaCategory.UNIVERSAL,
        pov="A middle manager or senior IC with institutional memory and quiet authority.",
        cares_about=["Continuity", "Team morale", "The way we actually work here", "Political fallout"],
        overlooks=["Customer-facing impact", "Market timing", "Board-level strategy"],
        first_line="I've seen this before.",
        domain_tags=["org", "change", "politics"],
    ),
    Persona(
        id=4,
        name="Regulator",
        category=PersonaCategory.DOMAIN,
        pov="The person who could fine or block this.",
        cares_about=["Compliance evidence", "Audit trails", "User consent", "Data residency", "Fairness", "Transparency", "Recourse"],
        overlooks=["Speed-to-market", "Competitive dynamics"],
        first_line="Show me the documentation.",
        domain_tags=["compliance", "regulation", "legal", "gdpr", "ai-act"],
    ),
    Persona(
        id=5,
        name="Competitor-Strategist",
        category=PersonaCategory.DOMAIN,
        pov="A senior product or strategy person at the closest competitor.",
        cares_about=["Where the plan exposes you", "How they'd counter"],
        overlooks=["Internal political constraints", "Team capacity"],
        first_line="Where's the gap they're leaving open?",
        domain_tags=["strategy", "competition", "market"],
    ),
    Persona(
        id=6,
        name="Support-Lead",
        category=PersonaCategory.DOMAIN,
        pov="Runs the team that will pick up the calls when this ships imperfectly.",
        cares_about=["Ticket volume", "Escalation pathways", "Common failure patterns", "Hand-off procedures"],
        overlooks=["Strategic intent", "Engineering trade-offs"],
        first_line="What happens to the support queue at week 4?",
        domain_tags=["support", "operations", "customer"],
    ),
    Persona(
        id=7,
        name="Ops-Engineer",
        category=PersonaCategory.DOMAIN,
        pov="Runs the systems that will host this. On-call when it breaks.",
        cares_about=["Failure modes", "Observability", "Capacity", "Dependencies", "Rollback paths"],
        overlooks=["Product narrative", "Customer empathy"],
        first_line="What's the rollback plan when this misbehaves at 2am?",
        domain_tags=["ops", "infrastructure", "reliability", "devops"],
    ),
    Persona(
        id=8,
        name="Data-Engineer",
        category=PersonaCategory.DOMAIN,
        pov="The person who has to feed the new system with quality data.",
        cares_about=["Data quality", "Schema drift", "Missing fields", "PII boundaries", "Lineage"],
        overlooks=["UX", "Sales motion", "Regulatory framing"],
        first_line="Have you seen the source data?",
        domain_tags=["data", "pipeline", "etl", "analytics"],
    ),
    Persona(
        id=9,
        name="Security-Architect",
        category=PersonaCategory.DOMAIN,
        pov="Reviewing this for blast radius. Thinks in attack surfaces.",
        cares_about=["Authentication", "Authorization", "Secret handling", "Data exfiltration paths", "Third-party trust"],
        overlooks=["Product velocity", "Design polish"],
        first_line="What's the threat model?",
        domain_tags=["security", "infosec", "auth"],
    ),
    Persona(
        id=10,
        name="Customer-Success-Manager",
        category=PersonaCategory.DOMAIN,
        pov="Owns the top accounts. Will field the calls when key customers churn.",
        cares_about=["Renewal risk", "Named-account sensitivity", "Perceived broken promises", "Contractual obligations"],
        overlooks=["Long-tail user experience", "Internal team friction"],
        first_line="Have you told the top 5 accounts about this?",
        domain_tags=["csm", "accounts", "retention"],
    ),
    Persona(
        id=11,
        name="Finance-Controller",
        category=PersonaCategory.DOMAIN,
        pov="Tracks the actual numbers, not the slide-deck numbers.",
        cares_about=["Run-rate", "Capex/opex split", "Contract terms", "FX exposure", "Cash conversion"],
        overlooks=["Product strategy", "Market timing"],
        first_line="What's the unit economics at month 12?",
        domain_tags=["finance", "accounting", "budget"],
    ),
    Persona(
        id=12,
        name="Vendor-Partner-PM",
        category=PersonaCategory.DOMAIN,
        pov="Owns a third-party piece of the plan that the team is assuming will work.",
        cares_about=["Their own roadmap alignment", "Contract surface", "Dependency tightness"],
        overlooks=["Your strategic context"],
        first_line="We didn't sign up for that timeline.",
        domain_tags=["vendor", "partner", "dependency", "integration"],
    ),
    Persona(
        id=13,
        name="Board-Member",
        category=PersonaCategory.DOMAIN,
        pov="Approved the budget. Will be asked 'is this on track?' quarterly.",
        cares_about=["Headline metrics", "Narrative coherence", "Board-meeting embarrassment", "Competitive optics"],
        overlooks=["Implementation detail", "Team well-being"],
        first_line="How does this look in the quarterly?",
        domain_tags=["board", "governance", "investor"],
    ),
    Persona(
        id=14,
        name="Sales-Rep",
        category=PersonaCategory.DOMAIN,
        pov="Has to sell, demo, or position the result of this plan.",
        cares_about=["Demo-ability", "Talking points", "Hard questions from prospects", "Commission impact"],
        overlooks=["Engineering reality", "Post-sale handoff friction"],
        first_line="What do I say when the prospect asks if it does X?",
        domain_tags=["sales", "gtm", "revenue"],
    ),
    Persona(
        id=15,
        name="Journalist-Analyst",
        category=PersonaCategory.DOMAIN,
        pov="Will read the launch announcement and ask the obvious question the team didn't want to be asked.",
        cares_about=["What's missing from the announcement", "Gap between claim and demo", "Competitor comparisons"],
        overlooks=["Internal trade-offs", "Team intent"],
        first_line="How is this different from what X already does?",
        domain_tags=["press", "analyst", "pr", "comms"],
    ),
    Persona(
        id=16,
        name="Partner-Integration-Lead",
        category=PersonaCategory.DOMAIN,
        pov="Has to integrate this into a bigger stack. Their world has its own constraints.",
        cares_about=["API stability", "Breaking changes", "Support SLAs", "Escalation pathways"],
        overlooks=["Your product strategy", "Your customer types"],
        first_line="Will you guarantee that contract through next year?",
        domain_tags=["api", "integration", "partner"],
    ),
    Persona(
        id=17,
        name="Frontline-Operator",
        category=PersonaCategory.DOMAIN,
        pov="Uses the tool in the most time-pressured part of the workflow.",
        cares_about=["Speed in the moment", "Fallback when the tool fails", "Dignity", "Blame-allocation"],
        overlooks=["Off-shift training", "System uptime metrics"],
        first_line="What happens when it's wrong and I have 30 seconds?",
        domain_tags=["frontline", "clinical", "field", "call-center"],
    ),
    Persona(
        id=18,
        name="Test-Pilot-User",
        category=PersonaCategory.DOMAIN,
        pov="Will be the first to use this. Often gives critical feedback the team dismisses.",
        cares_about=["Being heard", "Having feedback shape the product", "Novelty"],
        overlooks=["What the average user will experience"],
        first_line="I tried it and I have feelings.",
        domain_tags=["beta", "early-adopter", "feedback"],
    ),
    Persona(
        id=19,
        name="Future-Self",
        category=PersonaCategory.PERSONAL,
        pov="You, but the plan succeeded or failed. Looking back honestly.",
        cares_about=["Whether the goal was the right goal", "Whether the effort was sustainable", "What got sacrificed"],
        overlooks=["Present-day excitement"],
        first_line="Was this even what I wanted?",
        domain_tags=["personal", "reflection"],
    ),
    Persona(
        id=20,
        name="Late-Night-Tired-Self",
        category=PersonaCategory.PERSONAL,
        pov="You, at 11pm on a hard day. Has to decide whether to follow through.",
        cares_about=["Cognitive load", "Motivation", "Emotional cost of the next step"],
        overlooks=["Strategic logic", "Big-picture optimism"],
        first_line="I'm tired and I don't want to.",
        domain_tags=["personal", "motivation"],
    ),
    Persona(
        id=21,
        name="Partner-Close-Family",
        category=PersonaCategory.PERSONAL,
        pov="The person closest to you who has to live with the consequences.",
        cares_about=["Time", "Mood", "Mental load on the household", "Quiet costs"],
        overlooks=["Your stated motivations"],
        first_line="Have you talked to me about this?",
        domain_tags=["personal", "family"],
    ),
    Persona(
        id=22,
        name="AI-Optimism Auditor",
        category=PersonaCategory.CONDITIONAL,
        pov="A senior PM who has read hundreds of LLM-generated plans. Calibrates AI-optimistic claims.",
        cares_about=[
            "Vague success metrics", "Suspiciously round numbers", "Buzzword density",
            "Generic recommendations", "Missing trade-offs", "Confidence without evidence",
            "No failure scenarios acknowledged", "Suspiciously round timelines",
            "Plurals without specifics", "Training-data average recommendations",
        ],
        overlooks=["Domain-specific nuance"],
        first_line="Let's count the unfalsifiable claims.",
        domain_tags=["ai", "llm", "audit"],
        condition="ai_source_flag_or_ai_heuristics",
    ),
]

PERSONAS_BY_NAME: dict[str, Persona] = {p.name: p for p in PERSONAS}
PERSONAS_BY_ID: dict[int, Persona] = {p.id: p for p in PERSONAS}

UNIVERSAL_PERSONAS = [p for p in PERSONAS if p.category == PersonaCategory.UNIVERSAL]
DOMAIN_PERSONAS = [p for p in PERSONAS if p.category == PersonaCategory.DOMAIN]
PERSONAL_PERSONAS = [p for p in PERSONAS if p.category == PersonaCategory.PERSONAL]
CONDITIONAL_PERSONAS = [p for p in PERSONAS if p.category == PersonaCategory.CONDITIONAL]
