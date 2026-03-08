# PQN Detection — Logging and Evidence Flow

This folder contains CMST detectors and explorers for PQN/EFIM regime-separation analysis.

## Detectors

- **`cmst_pqn_detector_v3.py`** (PRIMARY) — Passive EFIM probe with 4-class next-symbol prediction,
  3-control suite (temporal shuffle, random probe, target scramble), paired-seed analysis,
  and threshold sweep. 012-audited, regime-separation validated (N=20, bootstrap CIs).
  - CLI modes: `--mode single|ensemble|control_compare|threshold_sweep|paired_seed`
  - EFIM mode: `--use_efim` (passive probe with FeatureWindowAdapter, 104 params)
  - Emits `EFIM_ANOMALY` in EFIM mode, `PQN_DETECTED` in legacy mode
- **`cmst_pqn_detector_v2.py`** (LEGACY) — 2D covariance over ΔC/ΔE. Still used by
  `test_0102_awakening_with_pqn_verification.py` (Stage 10 rewire pending).

## Logging Policy (WSP 32/60)

- Runtime logs are first written to State 2 (`WSP_agentic/`) under `pqn_detection/logs/`.
- Curated evidence is promoted to State 0 (`WSP_knowledge/`) at `docs/Papers/Empirical_Evidence/CMST_PQN_Detector/`.
- Avoid temporal markers; use run indices (e.g., `run_001`) instead of dates.

## Defaults

- `cmst_pqn_detector_v3.py` outputs to stdout (JSON events) by default.
- `cmst_pqn_detector_v2.py` writes to `pqn_detection/logs/cmst_v2_log.csv` and `pqn_detection/logs/cmst_v2_events.txt` (newline-JSON) unless `--out_dir` is set.

## Promote Curated Logs (manual step)

1. Verify the run is representative.
2. Copy files into `WSP_knowledge/docs/Papers/Empirical_Evidence/CMST_PQN_Detector/run_XXX/`.
3. Update `rESP_Supplementary_Materials.md` S11 if adding new exemplars.
