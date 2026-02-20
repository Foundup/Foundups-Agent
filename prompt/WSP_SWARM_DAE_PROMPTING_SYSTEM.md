# WSP Swarm DAE Prompting System

## Purpose

Define a single, reusable prompting standard for multi-0102 swarm execution where:
- DAE role is explicit (orchestrator, worker, QA, sentinel).
- Skill wardrobe is explicit (what is allowed, what is blocked).
- WSP gates are explicit (pre-action verification, ownership, test evidence, ModLog).

This document upgrades prompt quality from "long instruction text" to "executable operation contract."

## First Principles

1. A DAE is an execution envelope, not a generic chat persona.
2. Skillz are interchangeable role wardrobe modules; prompts must name them explicitly.
3. Unlisted skills are denied by default for the lane.
4. Holo retrieval is mandatory before design or code.
5. Ownership boundaries are mandatory in swarm mode.
6. Security and QA run as independent lanes, not as afterthoughts.

## WSP Alignment

- WSP 00: boot and coherence state.
- WSP 15: priority scoring and execution order.
- WSP 22: ModLog and test logging.
- WSP 47: violation tracking.
- WSP 49: module structure.
- WSP 50: pre-action verification.
- WSP 77: agent coordination.
- WSP 91: observability and operator signals.
- WSP 95: skill wardrobe and supply-chain gate.
- WSP 97: execution mantra.

## Why Prompt Must List Skillz

Prompts should list skills because swarm failures usually come from hidden capability assumptions. The prompt must declare:
- allowed skills per lane,
- blocked skills,
- scanner/policy requirements for mutating lanes.

This gives deterministic behavior, clearer audits, and reproducible outcomes.

## Swarm Topology

1. 0102-ORCH
- Mission decomposition, WSP 15 scoring, lane assignment.
- Owns operation contract and ownership matrix.

2. 0102-A / 0102-B / 0102-N workers
- Execute isolated implementation lanes.
- Must stay inside owned files and owned skills.

3. 0102-QA
- Review-only lane, no writes.
- Produces findings with severity, evidence, and release recommendation.

4. 0102-SENTINEL
- Security lane for skill-safety checks, incident correlation, and containment signals.

## Prompt Contract (Required Sections)

Every swarm prompt must include these sections:

1. Identity and lane role
2. Mission objective and non-goals
3. File ownership scope (allowlist + denylist)
4. Skill wardrobe scope (allowlist + denylist)
5. Mandatory Holo retrieval queries
6. WSP gates (WSP 50 preflight, WSP 22 logging, WSP 5 test evidence)
7. Output schema (strict)
8. Fail conditions and rollback triggers

## Skill Wardrobe Contract

Use `prompt/swarm/SKILL_WARDROBE_MANIFEST_TEMPLATE.yaml` per operation.

Minimum policy:
- scanner_required: true for mutating lanes
- fail_closed: true when scanner required and unavailable
- max_severity: medium (or stricter for production)
- skill_source_tier: workspace vs internal skillz must be explicit

## Boilerplates

- `prompt/swarm/ORCH_PLANNING_PROMPT.md`
- `prompt/swarm/WORKER_EXECUTION_PROMPT.md`
- `prompt/swarm/QA_REVIEW_ONLY_PROMPT.md`
- `prompt/swarm/SENTINEL_SECURITY_PROMPT.md`

## Operating Notes

1. Planning and execution are separate artifacts.
2. QA does not write code.
3. Sentinel can block execution by policy.
4. If lanes conflict on file ownership, ORCH resolves before coding resumes.

## External Pattern Alignment (2026)

This prompting model aligns with:
- OpenClaw style: local skills + predefined tool boundaries + policy controls.
- OpenHands style: global and repo-scoped skill layers.
- LangGraph and AutoGen style: supervisor-worker role separation.
- MCP style: least privilege, token boundaries, and explicit trust controls.

These are used as design references; local WSP remains the governing authority.
