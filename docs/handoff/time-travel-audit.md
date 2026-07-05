# Time-Travel Audit — 2026-07-05
**Scope:** time-travel.plugin v0.1.1 (markdown skill, 2,020 lines) + Plan-B handoff (Python engine, 137 tests).
**Verdict: CONDITIONAL.** The methodology is genuinely strong — better than typical premortem tooling. But you have a fork, a silent-failure risk, and one classification defect that would embarrass this tool in front of exactly the audience it's built for.

---

## What's good (keep)
- **The skill already IS the blueprint's §2c standard.** Progressive disclosure done right: phase-gated references, anti-patterns file, worked example. It should be the exemplar for restructuring your other skills, not a restructuring target.
- **Methodology is differentiated:** Confirmed/Inflated/Buried (evidence vs politics), rebuttal round, tripwires, "what would change my mind", per-lens max merging, "zero Buried risks = process failure". This is the moat.
- **`--fast` mode** shows token-consciousness was designed in, not bolted on.
- **Handoff doc quality:** flagging its own unspecced judgment calls (§3) is exactly the self-audit habit the retro loop needs.

## Critical findings

### C1 — The fork is now producing contradictory verdicts (highest priority)
Skill and engine are independent implementations that have already diverged on the core judgment:
- **Confirmed criteria** — Skill: specific formulation AND (analogue case OR internal signal OR cross-persona agreement). Engine: ≥2 personas with **exact/case-insensitive name match** AND ≥1 citation.
- **Rebuttal** — Skill: N parallel persona calls. Engine: 1 LLM call.
- **Buried sourcing** — Skill: Phase-4 political-signal analysis. Engine: Phase-1 blind-spot side-channel.
Same plan through both paths → different risk classes and different confidence numbers. For a decision-support tool, that's a defect, not a style choice.

### C2 — Engine classification defect: exact-name matching kills dedup
"Budget overrun" ≠ "Cost overrun" → never merges → cross-persona agreement almost never fires → most real risks land in **Inflated** → confidence math reads artificially high. The failure direction is *flattering to bad plans* — worst possible bias for a CXO premortem. Fix: semantic/fuzzy family matching (the skill's synthesis.md §1 already specifies the right logic; port it).

### C3 — Silent-failure mode on real LLM output
All 137 tests are stubbed; `_try_json` bare-excepts to `None` everywhere. Real model returns prose-wrapped or truncated JSON → sections silently come back **empty** → a CXO receives a confident, hollow report. Fix: real-provider smoke test (handoff §6.2) + fail-loud on empty phase output ("Phase 3 returned 0 claims — aborting" beats a polished empty report).

### C4 — Uncalibrated confidence percentages shown to executives
"Success probability 62% → 78%" from an unvalidated formula invites the one question that kills credibility: *"where does 62 come from?"* Fix (pick one): label it a qualitative confidence band (Low/Guarded/Moderate/High + drivers), or calibrate against 5–10 real premortems first. Don't ship raw percentages.

### C5 — Token goal vs skill architecture
Full run = 10–14 agent calls (5–7 personas ×2 rounds), each carrying full plan + evidence pack. On Cowork/Pro this contradicts the "minimum tokens" design goal. The **engine is the answer**: API-side persona calls routed to Haiku-class models cost pennies and don't touch plan quota. The skill's parallel-subagent fan-out is the expensive path.

### C6 — Audience/vehicle mismatch
"Management and CXOs run it" — but the polished path today is Claude Code CLI (they won't) and the Cowork skill path is the token-expensive one. Unresolved product question, not a code bug.

## Minor
- `superpowers:dispatching-parallel-agents` is an external plugin dependency — skill degrades if absent; add a fallback line.
- mypy's 7 errors sit in the provider adapters — the exact code real runs exercise and tests don't. Fix before smoke test, not after.
- Unpushed commit `a26ec51`.
- SKILL.md description ≈130 words — loads into every session (sprawl tax, blueprint §2c). Cut to 2 sentences + trigger verbs.

## Recommendation: unify with engine as reference implementation
Resolves handoff §6.3 and matches blueprint §2c ("deterministic work → scripts"):
1. **Engine = source of truth** for classification, dedup, confidence. Port skill's synthesis/classification semantics into it (fixes C1/C2).
2. **Skill = thin harness**: shells out to the engine when Python+keys available; falls back to `--fast` single-call markdown mode otherwise. Personas run on cheap API models (fixes C5).
3. **Exec one-pager becomes the default output** in Cowork; full report attached (addresses C6 for now).

## Ordered next steps
1. Fix C2 (fuzzy family matching) + port skill classification semantics into engine
2. mypy provider fixes → real-provider smoke test (C3), add fail-loud guards
3. Replace percentages with confidence bands or start calibration log (C4)
4. Wire skill→engine hybrid harness (C1/C5); push `a26ec51`
5. Then Plan C (CI, README, install script) — packaging polish after correctness

## Resolved architecture (decisions 2026-07-05: Cowork vehicle · plan-quota only · engine as truth)
**Split by work type:** LLM work in-session (quota), deterministic work in engine scripts (free).
- Engine's pure functions (dedup, classify, confidence, render) bundled as `scripts/` inside the Cowork plugin; run via sandbox Python. No API keys needed — engine never calls LLMs in this mode.
- Skill's markdown classification/synthesis rules are **deleted**; SKILL.md says "emit persona claims as JSON per schema → run `scripts/synthesize` → present output." Fork eliminated.
- Port the skill's (better) classification semantics + fuzzy family matching into the engine first (C1/C2), since engine is now the only judge.
- **Default mode = single structured call, all personas in one prompt** (~20% cost); `--deep` = parallel fan-out + rebuttal, reserved for board-level plans.
- Exec one-pager is the default Cowork output; full report + process log written as files.
- Contract test: JSON claim schema is the interface — one schema file, validated on both sides.

Revised next steps: (1) port classification semantics + fuzzy matching into engine, (2) define claim JSON schema + validator, (3) rewrite SKILL.md as thin harness with single-call default, (4) bundle engine pure functions into .plugin, test in Cowork sandbox, (5) confidence bands replace percentages, (6) push a26ec51, then Plan C.

## Blueprint impact
No structural changes — this validates it. Three additions:
- **§2c:** time-travel is the pilot/exemplar for skill restructuring (it's already 90% there).
- **§4:** retro loop also ingests time-travel run failures (real-provider issues → `failures.md` → engine patches).
- **§5:** persona fan-out = the canonical case for cheap-model routing via engine, off-quota.
