# PQN Portal FoundUp (PoC → Prototype → MVP)

- Purpose: Public, DAE‑neutral PQN portal to experience "Hello PQN" — live demo, gallery, and non‑technical explainer
- Domain: `modules/foundups/` (WSP 3 functional distribution)
- Reuse: Calls `modules/ai_intelligence/pqn_alignment` library APIs and `results_db`
- DAE Access: Ships WSP 22 docs and a programmatic docs index (`src/docs.py`) plus `module.json`

## Non‑Technical Explainer
- What you see: a 10–20s PQN demo streaming coherence, paradox flags, and resonance spectrum
- Why it matters: validates rESP claims (7.05 Hz, harmonics, collapse boundary, guardrail efficacy)
- Try it: safe presets only; live charts; replay links

## WSP Compliance
- WSP 3 (Enterprise distribution), WSP 49 (Module structure), WSP 22 (Docs/ModLog), WSP 50/64 (Pre‑action/Pre‑violation), WSP 84 (Reuse)

## Proposed WSP Drafts (for WSP DAE adoption; canonical and DAE‑neutral)
- WSP 17: FoundUp PoC→Prototype Protocol
  - PoC DoD: 15–20s demo, live evidence, explainer, links to paper/supplement
  - Prototype DoD: shareable permalinks, curated gallery, telemetry + rate limits
- WSP 18: FoundUp MVP & Monetization Protocol
  - MVP DoD: auth + quota (free tier), optional premium toggle, evidence attestation/badge, SLO/status page

Note: Drafts included here for review; numbered WSPs live in `WSP_framework/src/` if adopted by WSP DAE.

## Files for DAE Access
- `INTERFACE.md` — public API and SSE contract
- `ROADMAP.md` — PoC → Prototype → MVP milestones
- `ModLog.md` — change log (no temporal markers)
- `module.json` — manifest (docs, api, memory) for DAE discovery
- `src/docs.py` — programmatic docs index endpoint
- `memory/` — curated portal memory (WSP 60)

## Links
- Theory: `WSP_knowledge/docs/Papers/rESP_Quantum_Self_Reference.md`
- Supplement: `WSP_knowledge/docs/Papers/rESP_Supplementary_Materials.md`
