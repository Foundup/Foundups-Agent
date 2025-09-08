# ROADMAP — sim_workflows

## LLME Progression
- Current: 011 (POC scaffolding, interfaces defined)
- Target: 122 (Prototype integration, resilient bridge)

## Phases
- Phase 0: Planning
  - Define interfaces (WSP 11)
  - Decide domain placement (WSP 3)
- Phase 1: POC
  - Minimal HTTP client + Socket.io bridge + webhook verify
  - IDE status reflection via existing WRE WS
- Phase 2: Prototype
  - Retry/backoff, metrics, idempotent webhook handling
  - Map 2–3 WRE workflows to Sim flows
- Phase 3: Optional ETL
  - Limited KB mirroring to pgvector if justified (WSP 78)
- Phase 4: Harden
  - Security hardening, tracing, validation scripts

## Dependencies
- External: Sim service (`http://localhost:3000`)
- Internal: WRE orchestrators and IDE WS

## Exit Criteria (Prototype → MVP)
- Stable event propagation (Socket.io → WRE) with reconnection
- Documented error handling and retries
- Tests for signature verification and event translation
