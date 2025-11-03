# ricDAE Roadmap

## Vision
ricDAE supplies HoloDAE with a sovereign, continuously updated research intelligence feed. It ingests trusted sources, normalizes results into FoundUps knowledge graphs, and exposes MCP tools that drive autonomous orchestration (per WSP 37).

## Phases

### Phase 0 – Compliance Foundations (Now)
- Confirm module registration via HoloIndex and WSP 37 scoring
- Establish documentation set (README, ModLog, roadmap, tests skeleton)
- Define ingestion data contracts and directory layout (`data/raw`, `data/processed`, `research_index`)

### Phase 1 – Ingestion + Connector (P0, Orange Cube)
- Implement Gemini MCP connector and API client wrappers
- Configure git/API mirror jobs (google-research, deepmind, arXiv, Semantic Scholar)
- Add ToS guardrails and source registration workflow
- Emit ingestion telemetry for WSP 77 governance monitors

### Phase 2 – Normalization + Index (P1, Yellow Cube)
- Build normalization pipeline mapping metadata to FoundUps schemas
- Persist structured artifacts (`holo_index/research/`)
- Stand up vector + symbolic index with evaluation harness
- Provide regression tests validating ingestion + index coherence

### Phase 3 – MCP Tool Surface (P1)
- Implement MCP tools: `research_update`, `literature_search`, `trend_digest`, `source_register`
- Wire tool outputs into HoloDAE orchestrator workflows
- Add failure-handling + backpressure controls

### Phase 4 – Meta-Learning + Governance (P2, Green Cube)
- Launch trend digest + impact scoring (LLME + semantic narrative)
- Integrate meta-tool patterns for auto capability creation
- Expand compliance dashboards + ModLog automation

## Success Metrics
- [GREATER_EQUAL]95% ingestion job success rate (per source)
- <5 min latency from external release to internal availability
- Audit trail coverage 100% for source fetch -> MCP surfacing
- WSP 5/6 test suite coverage [GREATER_EQUAL]90%

## Dependencies
- ai_gateway (for outbound model calls)
- priority_scorer (to slot research tasks into roadmap)
- holo_index infrastructure

## Risks & Mitigations
- **Source policy changes** -> maintain modular connector definitions, switchable via config
- **Data drift** -> automated schema validation + alerting
- **Overload** -> throttle ingestion jobs by priority and maintain backlog metrics
