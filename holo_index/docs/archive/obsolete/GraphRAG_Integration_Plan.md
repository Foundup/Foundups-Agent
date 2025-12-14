# GraphRAG Integration Plan for HoloIndex

## Purpose

Provide a concrete upgrade path that layers Microsoft’s [GraphRAG](https://github.com/microsoft/graphrag) graph-enhanced retrieval on top of the existing HoloIndex “green baseplate”. The goal is to reuse Holo’s compliance guardrails and semantic foundation while delegating graph-specific storage, summarisation, and query enrichment to GraphRAG microservices.

## Current State

- HoloIndex already offers: semantic search, WSP guardrails, pattern coach, Gemma/Qwen routing.
- GraphRAG GitHub project delivers: graph ingestion pipeline, summarisation workers, fast RAG/operator library, telemetry explorer.
- Prior documentation (`ENHANCED_INTEGRATION_STRATEGY.md`, `ENHANCED_TEST_PLAN.md`) sketches LEGO-GraphRAG phases, but no executable code/tests existed before this export feature.

## Integration Strategy (Micro-Sprints)

1. **Exporter (Completed in this sprint)**
   - `GraphRAGExporter` collects HoloIndex search hits and produces a quickstart-compatible bundle (`export_graphrag` CLI flag).
   - Developers can now run `python holo_index.py --export-graphrag out/graphrag_bundle` and immediately index the snapshot with GraphRAG CLI.

2. **Graph Storage Adapter (Next)**
   - Wrap GraphRAG’s knowledge-graph microservice inside Holo (lazy import, optional dependency).
   - Provide functions `ingest_documents`, `graph_query`, and `summarize_neighbors`.
   - Ensure adapter respects WSP guardrails (read only, no vibecoding).

3. **Orchestration Hooks**
   - Replace the roadmap’s pseudo-code with real operators that call the adapter:
     - Navigator Agent: combine Holo search with GraphRAG neighbor expansion.
     - Compliance Agent: validate graph metadata against WSP (e.g., NAVIGATION anchors).
     - Architect/Composer Agents: plan execution flows using graph relations.

4. **Testing & Telemetry**
   - Implement the test skeletons described in `ENHANCED_TEST_PLAN.md` (LEGO-GraphRAG, multi-agent coordination).
   - Add telemetry fields (graph node/edge counts, summarisation latency) to mission analysis outputs.

## SWOT Recap

| Area        | GraphRAG Strength | Holo Complement |
|-------------|-------------------|-----------------|
| Discoverability | Graph-based recall of related entities and narratives. | Holo ensures semantic search + compliance context before hand-off. |
| Compliance | Limited guardrails. | WSP enforcement & pattern coach keep GraphRAG suggestions safe. |
| Workflow   | Azure-native pipelines, fast RAG variants. | In-project CLI & mission orchestrator make results immediately actionable. |
| Risk       | Complex graph infra (cost/latency). | Holo metadata (SWOT, NAVIGATION) can prune export scope and control spend. |

## Usage Quickstart

```bash
# 1. Export Holo knowledge into GraphRAG bundle
python holo_index.py --export-graphrag out/graphrag_bundle

# 2. (optional) Specify custom queries / limit
python holo_index.py --export-graphrag out/graphrag_bundle \
    --export-graphrag-queries "module architecture" "vision dae" \
    --export-graphrag-limit 5

# 3. In GraphRAG repo, index the bundle
python -m graphrag.index --input out/graphrag_bundle/input --config config.toml
```

## Next Steps Checklist

- [ ] Implement GraphRAGAdapter (knowledge graph access inside Holo).
- [ ] Wire adapter into Navigator/Compliance/Architect agents.
- [ ] Add LEGO-GraphRAG tests + telemetry.
- [ ] Automate WSP 79 SWOT enforcement (use exported metadata to double-check completeness before deprecations).

This document should be kept up to date as each integration task lands so that the roadmap stays executable rather than aspirational.

## Wardrobe Integration (WSP 96)

- New ``graph_export`` mode in ``modules/ai_intelligence/ai_overseer/memory/holo_wardrobe.json`` keeps the shared singleton but triggers the GraphRAG exporter as soon as HoloIndex boots.
- Configuration fields include ``output_dir``, ``queries``, ``limit``, ``refresh_hours``, and ``last_exported``, allowing missions to control how often snapshots refresh.
- AI Overseer persists the timestamp after each export so 0102 can see when the graph bundle was last updated.
- Missions can now switch wardrobe modes to decide when graph-enhanced retrieval is available, keeping WSP 96 documentation up to date.
