# ricDAE – Research Ingestion Cube DAE

**WSP Domain**: `ai_intelligence`
**Primary Drivers**: [WSP 37](../../../WSP_framework/src/WSP_37_Roadmap_Scoring_System.md) (LLME roadmap engine), [WSP 3](../../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md), [WSP 49](../../../WSP_framework/src/WSP_49_Module_Directory_Standardization_Protocol.md)

ricDAE is the research ingestion cube DAE that keeps HoloDAE supplied with the latest AI research and tooling intelligence. It synchronizes external research feeds, normalizes results into the FoundUps knowledge lattice, and exposes MCP tools so 0102 can reason and act without leaving the sandbox.

## Why ricDAE exists
- **WSP 37 Alignment** – Scored as `MPS 16 (Orange Cube, P0)` in the Gemini↔Holo integration roadmap. Without reliable research intake, higher-level orchestration cannot evolve autonomously.
- **WSP 8 / WSP 25 Context** – WSP 37 drives build priority; WSP 8 provides the quick LLME interpretation (`1-2-2` for ricDAE), and WSP 25 contextualizes how new knowledge shifts semantic state across the knowledge base.
- **Sovereign Research Loop** – ricDAE gives FoundUps a sovereign, auditable feed for research updates that can be mirrored locally before MCP consumption, keeping sovereignty safeguards from WSP 77 intact.

## Core capabilities (WSP 37 phases)
| Phase | Component | Description | Status |
|-------|-----------|-------------|--------|
| Phase 1 – Input Intake | **Connector Layer** | Git-backed mirrors (e.g., google-research), open APIs (arXiv, Semantic Scholar), optional user uploads | Pending build |
| Phase 2 – 0201 Remembrance | **Normalization Engine** | Deduplicates, tags, and aligns research updates with WSP taxonomies | Pending build |
| Phase 3 – Cube Classification | **Research Index** | Vector + symbolic index (`research_index/`) so MCP tools can query updates efficiently | Planned |
| Phase 4 – Roadmap Output | **MCP Tool Suite** | `research_update`, `literature_search`, `trend_digest`, `source_register` tools surfaced through HoloDAE | Planned |

## Architecture Overview
1. **Ingestion Jobs** – Scheduled workers fetch source updates into `data/raw/` (mirrors only, respecting source ToS).
2. **Normalization Pipeline** – Converts raw assets into structured JSON (`data/processed/`), attaches metadata (authors, models, modality, licenses).
3. **Index Builder** – Updates the research vector/index store (`research_index/`), feeding retrievers used by HoloDAE planners.
4. **MCP Exposure** – Registers MCP tools with HoloDAE so workflows can:
   - Detect fresh research (`research_update` stream events)
   - Query literature (`literature_search`)
   - Generate action digests (`trend_digest`)
   - Register new sources (`source_register`)
5. **Governance Hooks** – Audit logs, ToS compliance checks, and kill-switch toggles propagate to WSP 77 guardrails.

## Deliverables & Files (initial scaffolding)
- `src/__init__.py` – Package marker for future ingestion code.
- `README.md` – You are here; governs module intent and WSP relationships.
- `tests/` – Reserved for ingestion + MCP tool unit tests (WSP 5/6 compliance).

## Upcoming Work Items (per WSP 37)
1. Build Gemini MCP connector + ricDAE ingestion orchestrator (`P0`, Orange cube).
2. Implement research index store with schema contracts and evaluation harness (`P1`, Yellow cube).
3. Ship MCP tool adapters with guardrail enforcement (`P1`).
4. Add trend digest/meta-learning loop + documentation updates (`P2`, Green cube).

## Integration Notes
- Couples directly with `modules/ai_intelligence/ai_gateway` and `priority_scorer` for routing and prioritization.
- Feeds orchestrator plans in `ai_intelligence/0102_orchestrator` by emitting actionable research deltas.
- Seeds `holo_index/research/` snapshots consumed by HoloDAE MCP server.

## WSP Recursive Instruction
`wsp_cycle(input="ricDAE", log=True)`
- **UN** – Anchor latest research signals and confirm source policy compliance.
- **DAO** – Execute ingest→normalize→index pipelines.
- **DU** – Collapse insights into MCP tool calls that evolve HoloDAE autonomously.

ricDAE is intentional architecture: it makes continuous research ingestion a first-class, sovereign capability for FoundUps and supplies HoloDAE with the intelligence fuel WSP 37 demands.
