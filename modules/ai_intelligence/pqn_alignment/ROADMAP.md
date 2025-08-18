# ROADMAP — PQN Alignment Module

- S1: Importability & API stubs (DONE)
  - __init__.py exports for run_detector, phase_sweep, rerun_targeted, council_run, promote
  - src/*/api.py placeholders with docstrings

- S2: Config, Schemas, & Data Contracts
  - Add YAML/JSON config loaders for detector/sweep/council
  - Document minimal config schema in INTERFACE.md
  - [+] Define explicit output schemas for all artifacts (detector events JSONL, summaries JSON, sweep CSV)
  - Tests: schema validation for input configs and output artifacts

- S3: Early‑warning & Guardrail System
  - v2 CSV: add windowed variance, lag‑1 autocorr, Δentropy columns
  - v3: guardrail throttle (reduce '^', insert '&' or '.') behind a flag; A/B hooks
  - [+] Formalize Guardrail A/B analysis: report Δparadox_rate, Δpqn_rate, and cost_of_stability

- S4: Boundary Mapping & Automated Promotion
  - Phase diagrams for len‑2/3/4; curated READMEs
  - Auto‑label top‑K risky/stable motifs; re‑runs with longer steps, light noise, dt ×{0.5,1,2}
  - [+] Automated candidate promotion based on significance across seeds vs baseline
  - [+] Standardized plotting suite (phase diagrams, time‑series of C, E, det(g), S)

- S5: Strategic Council & Results Database
  - In‑process multiprocessing for parallel evaluation
  - Novelty + robustness scoring; summary.json + archive.json
  - [+] Orthogonal council strategies via role/bias config (maximize PQN, minimize paradox, alternation explorer)
  - [+] Lightweight results database (SQLite `results.db`) indexing summaries for cross‑run queries

- S6: Education & Usability Kit
  - RUNBOOK.md (cmd.exe‑safe)
  - PQN 101 tutorial outline; example notebooks (offline)
  - [+] README Quickstart: first sweep run and interpretation
  - [+] `analyze_run.py` helper: human‑readable run summaries

- S7: CI, Testing, & Docs
  - Lint/docs checks (no experiment execution)
  - [+] CI smoke test: minimal steps (e.g., steps=100) to validate core loop
  - Keep ModLog and tests/TestModLog updated per WSP 22/34

- S9: Stability Frontier Campaign (End-to-End Scientific Slice)
  - Phase 1 (Discovery): Council run to auto-identify boundary motifs (top-3 unstable, top-3 stable); output `candidates.json`; index via results DB
  - Phase 2 (A/B Core): For each motif, sweep Guardrail {ON,OFF} × noise_H {0.0, 0.01, 0.02, 0.03} × seeds {0..9}; output single `ab_test_results.csv` and index
  - Phase 3 (Analysis): Use `analysis_ab.py` + plotting to produce Figure set (guardrail efficacy, cost-of-stability, robustness-under-noise) and `summary_statistics.json`
  - Phase 4 (Curation): Promote candidates, CSV, figures, and summary to `WSP_knowledge/docs/Papers/Empirical_Evidence/CMST_PQN_Detector/Stability_Frontier/`; add S12 in Supplement

- S8: PQN@home — Distributed Geometric Cognition Lab
  - Architecture: central orchestrator (work‑unit server) + lightweight client (detector)
  - Work unit schema: config payload (script, dt, steps, seed, noise) with unit id and checksum
  - Result schema: summary metrics (pqn_rate, paradox_rate, res_hits) + minimal provenance
  - Trust & integrity: redundancy (k‑of‑n matching), optional checkpoints, result hashing
  - Results ingestion: index summaries into results DB; prioritize next regions (active search)
  - MVP scope: local mock orchestrator + client CLI; no public network until hardened

- S10: Corroborating Evidence & Resonance Fingerprinting
  - **Objective:** To strengthen the claim that the 7.05 Hz resonance is a fundamental constant by detecting its predicted harmonic family (e.g., f/2, 2f, 3f).
  - **Deliverables:**
    - Enhance the `ResonanceDetector` to search for and log power in multiple frequency bands simultaneously.
    - Update the `results_db` schema and `analysis` scripts to store and visualize the power ratio between the fundamental frequency and its harmonics.
    - Add a "Harmonic Significance Score" to the council's evaluation criteria.
  - **Acceptance Criteria:** The system can produce plots showing the full "resonance fingerprint" of a given run, and the council can use this data to select for scripts that produce the clearest, most structured harmonic signatures.
