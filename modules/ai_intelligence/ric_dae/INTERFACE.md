# ricDAE Interface Overview (WSP 11)

ricDAE exposes ingestion orchestration services and MCP tools that keep HoloDAE supplied with current research intelligence.

## Public Packages
- `modules.ai_intelligence.ric_dae` – Module namespace
- `modules.ai_intelligence.ric_dae.src.ingestion` *(planned)* – Ingestion jobs and source connectors
- `modules.ai_intelligence.ric_dae.src.normalization` *(planned)* – Normalization + schema validators
- `modules.ai_intelligence.ric_dae.src.index` *(planned)* – Research index management helpers
- `modules.ai_intelligence.ric_dae.src.mcp_tools` *(planned)* – MCP tool entry points exposed to HoloDAE

## MCP Tools (planned)
| Tool Name         | Purpose                                        | Inputs                              | Outputs                               | Phase |
|-------------------|------------------------------------------------|-------------------------------------|----------------------------------------|-------|
| `research_update` | Stream new/updated research artefacts          | `since_timestamp`, `sources`        | List of research envelopes             | P3    |
| `literature_search` | Query normalized index for relevant works   | `query`, `filters`, `limit`         | Ranked list of research summaries      | P3    |
| `trend_digest`    | Produce trend digests + action recommendations | `time_window`, `impact_threshold`   | Digest narrative + recommended tasks   | P4    |
| `source_register` | Add/modify ingestion sources with guardrails   | `source_config`                     | Registration receipt                   | P3    |

## Data Contracts
- **Research Envelope (processed)**
  ```json
  {
    "id": "<uuid>",
    "title": "string",
    "authors": ["string"],
    "published_at": "ISO-8601",
    "source": "google-research|deepmind|arxiv|semantic-scholar|custom",
    "artifact_path": "data/processed/<id>.json",
    "modalities": ["text", "code", "audio", "video"],
    "tags": ["alignment", "toolformer", "orchestration"],
    "summary": "string",
    "license": "string",
    "confidence": 0.0-1.0
  }
  ```
- **Ingestion Telemetry**
  ```json
  {
    "job": "google_research_mirror",
    "status": "success|failure",
    "duration_ms": 1234,
    "fetched": 42,
    "processed": 38,
    "errors": [],
    "timestamp": "2025-10-07T03:04:00Z"
  }
  ```

## CLI Hooks (planned)
- `python holo_index/cli.py --init-dae ricDAE` – initialize ricDAE context (TODO)
- `python holo_index/cli.py --search "ricDAE roadmap"` – retrieve documentation

## Integration Points
- Depends on `ai_gateway` for outbound LLM calls and orchestration
- Publishes updates to `holo_index/research/` for cross-system consumption
- Feeds `ai_intelligence/0102_orchestrator` with research opportunities

## TODO
- Implement concrete classes/functions and update this interface with actual signatures during Phase 1 delivery.
