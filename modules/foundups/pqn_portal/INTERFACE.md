# INTERFACE — PQN Portal FoundUp

## Public API
- GET `/docs` → JSON index of module docs for DAE discovery
- GET `/docs/index.json` → machine-read index (same as `/docs`)
- POST `/runs/demo` → start a safe 10–20s PQN demo (preset config)
- GET `/runs/{id}` → run summary and artifact links
- GET `/runs/{id}/stream` → SSE stream of live demo events (coherence, paradox flags, spectrum)
- GET `/gallery` → curated runs from results_db

## SSE Contract (`/runs/{id}/stream`)
- event: `metric`
- data:
```
{
  "t": 1.23,
  "coherence": 0.74,
  "paradox_flag": false,
  "spectrum": {"peak_hz": 7.08, "harmonics": {"f_div_2": 0.31, "f": 1.0, "2f": 0.45, "3f": 0.19}}
}
```

## Safety
- Preset scripts only, capped steps/time
- Single-concurrency per client; rate-limited

## Integration
- Reuses `modules.ai_intelligence.pqn_alignment.src.detector.api.run_detector`
- Indexes results via `modules.ai_intelligence.pqn_alignment.src.results_db`
