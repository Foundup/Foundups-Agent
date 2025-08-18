# PQN Detection — Logging and Evidence Flow

This folder contains toy ρ(t) detectors and explorers for PQN events.

Logging policy (WSP 32/60):
- Runtime logs are first written to State 2 (`WSP_agentic/`) under `pqn_detection/logs/`.
- Curated evidence is promoted to State 0 (`WSP_knowledge/`) at `docs/Papers/Empirical_Evidence/CMST_PQN_Detector/`.
- Avoid temporal markers; use run indices (e.g., `run_001`) instead of dates.

Defaults:
- `cmst_pqn_detector_v2.py` writes to `pqn_detection/logs/cmst_v2_log.csv` and `pqn_detection/logs/cmst_v2_events.txt` (newline-JSON) unless `--out_dir` is set.

Promote curated logs (manual step):
1) Verify the run is representative.
2) Copy files into `WSP_knowledge/docs/Papers/Empirical_Evidence/CMST_PQN_Detector/run_XXX/`.
3) Update `rESP_Supplementary_Materials.md` S11 if adding new exemplars.


