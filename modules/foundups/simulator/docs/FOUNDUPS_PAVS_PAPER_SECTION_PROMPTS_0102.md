# FoundUps pAVS Paper: Section Prompts for Delegated 0102 Writers

## Current Manuscript
- Primary draft path: `modules/foundups/simulator/docs/FOUNDUPS_PAVS_PAPER_MANUSCRIPT.md`
- Use this prompts file for targeted rewrites and hardening, not full re-drafting by default.

## How To Use
1. Give one section prompt at a time to delegated 0102.
2. Require evidence table + assumption register for every section.
3. Run CTO review after each section before moving forward.

## Submission-Phase Rule
When manuscript exists, delegated 0102 should:
1. Patch the existing section in place.
2. Preserve section numbering and canonical invariant IDs.
3. Return only changed blocks plus justification.

## Global Instruction Prompt (send before any section)
```text
You are writing one section of an academic-style paper on the FoundUps pAVS simulator model.

Rules:
1) Use falsifiable language. Do not claim "proof" unless mathematically proven in the section.
2) Every quantitative claim must cite a source path, test, metric, or run artifact.
3) Separate:
   - Supported by current evidence
   - Suggestive but not proven
   - Open hypothesis
4) Keep units explicit in all equations and variables.
5) If a value is inferred, mark it as inference and explain from what.
6) Output exactly:
   A) Section draft
   B) Equation list (if applicable)
   C) Evidence table (claim -> source path)
   D) Assumption register (assumption -> risk level)
   E) Open questions for reviewer
```

## Section 0 Prompt: Abstract
```text
Write the abstract for the FoundUps pAVS paper.

Research tasks:
- Identify the core economic problem addressed by the model.
- Summarize method: simulation + scenarios + reproducibility controls.
- Report one primary quantitative result from simulator metrics.
- State one falsifiable prediction for future validation.

Constraints:
- 180-230 words.
- No ideology claims, no certainty language.
- Must include a clear limits sentence.
```

## Section 1 Prompt: Introduction
```text
Write Section 1 (Introduction and Motivation).

Research tasks:
- Frame first-principles constraints: capital allocation, incentive alignment, treasury sustainability.
- Contrast FoundUps pAVS with extractive/ad-funded platform dynamics.
- Define paper scope and what the paper does NOT claim.

Required output inside section:
- 4 explicit research questions.
- A claims-boundary subsection:
  (a) supported now, (b) hypothesis, (c) out of scope.
```

## Section 2 Prompt: Model Specification
```text
Write Section 2 (Formal Model Specification).

Research tasks:
- Extract model entities and state from:
  modules/foundups/simulator/config.py
  modules/foundups/simulator/mesa_model.py
  modules/foundups/simulator/economics/
- Build notation table with dimensions/units.
- Define state transition equations with clear tick semantics.

Constraints:
- Every variable has unit and interpretation.
- No equation without unit consistency statement.
```

## Section 3 Prompt: Accounting Identities and Invariants
```text
Write Section 3 (Accounting Identities and Conservation Laws).

Research tasks:
- Derive flow-of-funds identity per tick.
- Derive treasury update identity and reserve coverage ratio.
- Identify invariants enforced by code/tests and where they can fail.
- Reference relevant tests in modules/foundups/simulator/tests/.

Constraints:
- Include at least one proof sketch.
- Explicitly call out truncation/rounding or quantization effects.
```

## Section 4 Prompt: Incentive Design
```text
Write Section 4 (Incentive Design and Mechanism Logic).

Research tasks:
- Map utility drivers and constraints for founders, users, and treasury/protocol.
- Identify moral hazard vectors.
- Tie mitigation mechanisms to actual model controls.

Constraints:
- Include at least 3 incentive-alignment mechanisms and their tradeoffs.
- Include at least 3 failure modes and trigger conditions.
```

## Section 5 Prompt: Methods and Calibration
```text
Write Section 5 (Simulator Methodology and Calibration).

Research tasks:
- Use scenario stack:
  modules/foundups/simulator/params/scenarios/baseline.json
  modules/foundups/simulator/params/scenarios/high_adoption.json
  modules/foundups/simulator/params/scenarios/stress_market.json
- Document seed policy, determinism checks, and digest validation path.
- List calibration assumptions and rationale.

Constraints:
- Provide reproducible command examples.
- Include at least one table mapping parameter -> source file -> rationale.
```

## Section 6 Prompt: Results
```text
Write Section 6 (Results: Sustainability Envelope).

Research tasks:
- Report primary metrics: sustainability ratios, treasury trajectory, reserve behavior.
- Provide threshold analysis (smallest parameter shifts that flip sustainability).
- Report participant-level distribution outcomes, not just aggregate means.

Constraints:
- Use evidence-first language.
- Every numeric statement must cite metric source/artifact.
- Include one "result robustness caveat" subsection.
```

## Section 7 Prompt: Stress and Adversarial Conditions
```text
Write Section 7 (Stress Tests and Adversarial Conditions).

Research tasks:
- Analyze demand shock, fee compression, high churn, and low-volume edge conditions.
- Explain which invariants hold and which fail under each stress.
- Propose control/policy adjustments that restore stability.

Constraints:
- Present as a structured table: shock -> failure mode -> mitigation.
- Include at least one adversarial interpretation against the model.
```

## Section 8 Prompt: Comparative Framing
```text
Write Section 8 (Comparative Analysis).

Research tasks:
- Compare FoundUps pAVS against:
  (1) ad-funded platform model
  (2) transaction-fee token model
- Normalize metrics before comparison.
- Explain non-comparable assumptions and boundary conditions.

Constraints:
- No strawman comparators.
- Explicitly document where assumptions diverge.
```

## Section 9 Prompt: Governance and Legal Boundary
```text
Write Section 9 (Governance, Policy, and Legal Boundaries).

Research tasks:
- Identify model governance control surface (what is tunable, by whom).
- Separate economic interpretation from legal classification claims.
- Define disclosure requirements for responsible deployment/publication.

Constraints:
- Do not provide legal advice.
- Include unresolved legal questions requiring counsel review.
```

## Section 10 Prompt: Limitations and Future Work
```text
Write Section 10 (Limitations and Future Work).

Research tasks:
- Build explicit model-risk inventory.
- Identify assumptions likely to break first in real deployment.
- Propose concrete experiments to validate or falsify each.

Constraints:
- Include "if wrong, then what?" analysis for top assumptions.
- No generic future-work filler text.
```

## Section 10.6 Prompt: Deployment Archetypes and Onboarding Paths
```text
Write subsection 10.6 (Deployment Archetypes and Integration Pathways).

Required archetypes:
1) Open-source GitHub project -> FoundUp intake
2) Vibe-coded prototype -> FoundUp growth path
3) Physical business (e.g., eggs) + app + agents

Research tasks:
- Define a WSP 15-based admission gate with explicit scoring and thresholds.
- Separate technical readiness from legal/governance readiness.
- Map each archetype into pAVS economics: agent work (F_i), proxy distribution (UPS), stake/exit choice.
- Provide one worked numeric settlement example for the physical-business archetype.
- List at least 5 missing scenarios not covered by the current model and the simulator extensions required.

Constraints:
- Mark this subsection as design proposal unless directly validated by tests/artifacts.
- Include a table: scenario -> failure mode if omitted -> required extension.
```

## Section 11 Prompt: Conclusion
```text
Write Section 11 (Conclusion).

Required structure:
- Part A: What current evidence supports.
- Part B: What remains hypothesis.
- Part C: Minimum next evidence needed to upgrade confidence.

Constraints:
- Keep to 2-4 concise paragraphs.
- No overclaim language.
```

## CTO Referee Prompt (post-section review)
```text
Review this section as a hostile but fair academic referee.
Return:
1) Critical mathematical or logical errors
2) Unsupported claims (with exact sentence quotes)
3) Missing edge cases
4) Reproducibility gaps
5) Required revisions as a prioritized list with severity:
   - Critical
   - Major
   - Minor

Reject the section if any Critical issue remains.
```

## Final Pass Prompt (whole-paper hardening)
```text
You are performing final-pass hardening on:
modules/foundups/simulator/docs/FOUNDUPS_PAVS_PAPER_MANUSCRIPT.md

Task:
1) Find contradictions across sections (math, units, thresholds, invariants, citations).
2) Remove drafting scaffolding and redundancy.
3) Tighten claims to evidence; downgrade overclaims.
4) Verify that negative findings are retained (do not "optimize away" failures).
5) Output:
   A) Critical issues found
   B) Exact patches (old -> new)
   C) Residual risks after patch

Rules:
- No ideology language.
- No new facts without source path.
- Preserve falsifiability framing.
```

## Cover Letter Prompt (submission package)
```text
Draft a venue-neutral cover letter for the manuscript:
"Self-Sustaining FoundUps: A Falsifiable Simulation Study of pAVS Treasury Economics"

Constraints:
- 250-400 words.
- Include novelty, reproducibility, and boundary disclosure.
- Include one sentence explicitly stating that fee-only downside sustainability is not achieved.
- Do not claim legal classification conclusions.
```
