# HoloIndex Machine-Language Specification (0102)

## 1) First-Principles Definition
HoloIndex is a deterministic retrieval-and-orchestration machine:

`(query, context, configuration) -> (ranked memory hits, protocol guidance, action surface)`

It is not only a search utility. It is a policy-bearing retrieval system with:
- memory indexing,
- intent routing,
- compliance framing,
- agent-specific output compression.

## 2) Canonical Runtime Topology
- Retrieval core: `holo_index/core/holo_index.py` (`HoloIndex`)
- CLI command router: `holo_index/cli.py`
- Intent and composition:
  - `holo_index/intent_classifier.py`
  - `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py`
  - `holo_index/output_composer.py`
- Output contract + memory cards: `holo_index/output/agentic_output_throttler.py`
- Adaptive learning:
  - `holo_index/feedback_learner.py`
  - `holo_index/adaptive_learning/breadcrumb_tracer.py`

## 3) State Machine
- `BOOTSTRAP`: initialize model, Chroma collections, cached WSP summary/navigation.
- `INDEX_READY`: accepts index/search commands.
- `SEARCH_EXECUTING`: dual retrieval (code + WSP + optional tests/skills/symbols).
- `RESULT_FOUND`: at least one hit.
- `RESULT_MISSING`: no hit, creation guidance path.
- `ERROR`: exception path with structured fallback payload.

Transition truth is encoded in `holo_index/core/holo_index.py:1014` and `holo_index/output/agentic_output_throttler.py:427`.

## 4) Scoring Math (Current)
- Vector distance conversion:
  - `similarity = 1 / (1 + distance)`
- Similarity floor:
  - `HOLO_MIN_SIMILARITY` (default `0.35`)
- Hybrid rank:
  - `score = 0.5*priority + 0.3*similarity + 0.2*keyword_score`
- Skill rank variant:
  - `score = 0.6*priority + 0.3*similarity + 0.1*keyword_score`
- Lexical fallback similarity:
  - `similarity = min(1.0, keyword_score / (max(1, token_count * 2.5)))`

## 5) Retrieval Contract (Machine Surface)
`search(query, limit, doc_type_filter)` returns keys:
- `code_hits`, `wsp_hits`, `test_hits`
- `code`, `wsps`, `tests` (legacy compatibility)
- `skills`, `skill_hits`
- `metadata` with counts and timestamp

`--bundle-json` returns schema `wsp_memory_bundle_v1`:
- `schema_version`, `generated_at`, `ok`
- `task`, `module_hint`, `module_path`
- `structured_memory`, `task_retrieval`

## 6) Intent-Orchestration Contract
Intent classes:
- `doc_lookup`
- `code_location`
- `module_health`
- `research`
- `general`

Execution components:
- `health_analysis`
- `vibecoding_analysis`
- `file_size_monitor`
- `module_analysis`
- `pattern_coach`
- `orphan_analysis`
- `wsp_documentation_guardian`

MCP research is intent-gated (`research` only).

## 7) CTO Consistency Audit (Docs vs Runtime)
Validated on 2026-02-18 with tests:
- `holo_index/tests/test_intent_classifier.py`
- `holo_index/tests/test_output_composer.py`
- `holo_index/tests/test_memory_output_contract.py`
- `holo_index/tests/test_doc_type_filtering.py`

Result: `45 passed`.

Resolved drifts:
- `OutputComposer` accepted only `intent_classification`; now supports legacy `intent` callers.
- Router returned non-executable component names (`code_index_search`, `mcp_integration`); now aligned to executable component surface.
- `HoloIndex.search()` now handles partial initialization without collapsing into exception fallback.
- Intent classification and alert grouping now match expected behavioral contract.

Open drift:
- `CLI_REFERENCE.md` is a menu snapshot, not an exhaustive flag contract. This file + JSON spec are now the canonical machine contract.

## 8) Economic/System Interpretation
At system level, HoloIndex optimizes:
- recall of existing implementations,
- policy adherence (WSP constraints),
- token efficiency under agent context limits.

It behaves as a constrained optimizer:
- maximize relevance and protocol utility,
- subject to output and latency constraints.

## 9) Canonical Source of Truth
- Machine contract (authoritative, executable-facing): `holo_index/docs/HOLO_INDEX_MACHINE_LANGUAGE_SPEC_0102.json`
- Human-readable explanation: this document
- Public interface summary: `holo_index/INTERFACE.md`
- Operator/menu atlas (non-normative): `holo_index/CLI_REFERENCE.md`
