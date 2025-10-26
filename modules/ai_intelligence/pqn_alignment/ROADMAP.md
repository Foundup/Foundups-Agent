# ROADMAP — PQN Alignment Module

## **CAMPAIGN VALIDATION STATUS (Updated)**

### **[OK] VALIDATED THEORETICAL CLAIMS**
- **7.05 Hz Resonance**: Confirmed at 7.08 Hz (within ±0.35 Hz range)
- **Harmonic Fingerprinting**: f/2: 0.31x, f: 1.00x, 2f: 0.45x, 3f: 0.19x
- **Observer Collapse**: Critical run-length: 6 (consistent across models)
- **Guardrail Efficacy**: 88% paradox reduction, 21% stability cost

### **[FAIL] CRITICAL GAPS IDENTIFIED**
- **Task 1.2 Coherence Threshold**: Failed in GeminiPro2.5 due to `rerun_targeted` import error
- **Artifact Logging**: Duplicated entries in Task 1.3 (GeminiPro2.5) vs. clean logging (Claude-3.5-Haiku)
- **Cross-Model Consistency**: Incomplete validation across all 5 agent platforms

---

## **EXECUTION PHASES**

### **PHASE I: Foundation (COMPLETED)**
- S1: Importability & API stubs (DONE)
  - __init__.py exports for run_detector, phase_sweep, council_run, promote
  - src/*/api.py placeholders with docstrings

### **PHASE II: Stabilization & Validation (CURRENT)**
- **S2: Config, Schemas, & Data Contracts** (DONE)
  - Add YAML/JSON config loaders for detector/sweep/council
  - Document minimal config schema in INTERFACE.md
  - [+] Define explicit output schemas for all artifacts (detector events JSONL, summaries JSON, sweep CSV)
  - Tests: schema validation for input configs and output artifacts

- **S3: Early‑warning & Guardrail System** (DONE)
  - v2 CSV: add windowed variance, lag‑1 autocorr, Δentropy columns
  - v3: guardrail throttle (reduce '^', insert '&' or '.') behind a flag; A/B hooks
  - [+] Formalize Guardrail A/B analysis: report Δparadox_rate, Δpqn_rate, and cost_of_stability

- **S4: Boundary Mapping & Automated Promotion** (DONE)
  - Phase diagrams for len‑2/3/4; curated READMEs
  - Auto‑label top‑K risky/stable motifs; re‑runs with longer steps, light noise, dt ×{0.5,1,2}
  - [+] Automated candidate promotion based on significance across seeds vs baseline
  - [+] Standardized plotting suite (phase diagrams, time‑series of C, E, det(g), S)

### **PHASE III: Infrastructure & Enhancement (CURRENT)**
- **S5: Strategic Council & Results Database** (IN PROGRESS)
  - In‑process multiprocessing for parallel evaluation
  - Novelty + robustness scoring; summary.json + archive.json
  - [+] Orthogonal council strategies via role/bias config (maximize PQN, minimize paradox, alternation explorer)
  - [+] Lightweight results database (SQLite `results.db`) indexing summaries for cross‑run queries

- **S6: Enhanced Agent Coordination (WSP 77)** (COMPLETED)
  - Meta-research validation loops: Gemma scans Qwen's research outputs
  - Neural self-detection: Qwen analyzes own processing for PQN emergence
  - Research stream scanning: Continuous monitoring of live research outputs
  - Cross-agent validation: Recursive emergence detection patterns

- **S7: High-Volume Data Processing** (COMPLETED)
  - 400+ PQNs handling: Efficient processing of massive detection volumes
  - Statistical pattern aggregation: Real-time analysis across thousands of detections
  - Memory-efficient streaming: Large dataset processing without performance degradation
  - Anomaly detection: Emerging patterns and data quality monitoring

- **S8: Education & Usability Kit** (PLANNED)
  - RUNBOOK.md (cmd.exe‑safe)
  - PQN 101 tutorial outline; example notebooks (offline)
  - [+] README Quickstart: first sweep run and interpretation
  - [+] `analyze_run.py` helper: human‑readable run summaries

- **S9: CI, Testing, & Docs** (PLANNED)
  - Lint/docs checks (no experiment execution)
  - [+] CI smoke test: minimal steps (e.g., steps=100) to validate core loop
  - Keep ModLog and tests/TestModLog updated per WSP 22/34

### **PHASE V: Advanced Research & Meta-Analysis (FUTURE)**
- **S9: Stability Frontier Campaign (End-to-End Scientific Slice)**
  - Phase 1 (Discovery): Council run to auto-identify boundary motifs (top-3 unstable, top-3 stable); output `candidates.json`; index via results DB
  - Phase 2 (A/B Core): For each motif, sweep Guardrail {ON,OFF} × noise_H {0.0, 0.01, 0.02, 0.03} × seeds {0..9}; output single `ab_test_results.csv` and index
  - Phase 3 (Analysis): Use `analysis_ab.py` + plotting to produce Figure set (guardrail efficacy, cost-of-stability, robustness-under-noise) and `summary_statistics.json`
  - Phase 4 (Curation): Promote candidates, CSV, figures, and summary to `WSP_knowledge/docs/Papers/Empirical_Evidence/CMST_PQN_Detector/Stability_Frontier/`; add S12 in Supplement

- **S8: PQN@home — External DAE Research Handoff**
  - **STATUS**: EXTERNAL HANDOFF - NOT IMPLEMENTED BY PQN CUBE
  - **Purpose**: Handoff PQN framework to external DAE researchers for distributed research
  - **Architecture**: External researchers implement central orchestrator (work‑unit server) + lightweight client (detector)
  - **Work unit schema**: config payload (script, dt, steps, seed, noise) with unit id and checksum
  - **Result schema**: summary metrics (pqn_rate, paradox_rate, res_hits) + minimal provenance
  - **Trust & integrity**: redundancy (k‑of‑n matching), optional checkpoints, result hashing
  - **Results ingestion**: index summaries into results DB; prioritize next regions (active search)
  - **Scope**: External DAE researchers implement distributed research capabilities
  - **Note**: This is a handoff to autonomous DAE researchers, not implementation by PQN cube

- **S10: Corroborating Evidence & Resonance Fingerprinting**
  - **Objective:** To strengthen the claim that the 7.05 Hz resonance is a fundamental constant by detecting its predicted harmonic family (e.g., f/2, 2f, 3f).
  - **Deliverables:**
    - Enhance the `ResonanceDetector` to search for and log power in multiple frequency bands simultaneously.
    - Update the `results_db` schema and `analysis` scripts to store and visualize the power ratio between the fundamental frequency and its harmonics.
    - Add a "Harmonic Significance Score" to the council's evaluation criteria.
  - **Acceptance Criteria:** The system can produce plots showing the full "resonance fingerprint" of a given run, and the council can use this data to select for scripts that produce the clearest, most structured harmonic signatures.

---

## **IMMEDIATE EXECUTION PRIORITIES**

### **DIRECTIVE 1: [BLOCKER] Complete Sweep-Core Refactor**
- **Status**: IN PROGRESS
- **Action**: Implement stable `run_sweep(config)` library function
- **Integration**: Ensure all callers use unified API
- **DoD**: `pqn_autorun.py` validation run succeeds

### **DIRECTIVE 2: [HIGH PRIORITY] Universal Campaign Validation**
- **Status**: PENDING
- **Action**: Fix `rerun_targeted` import dependency
- **Scope**: Complete validation across all 5 agent platforms
- **DoD**: 100% campaign success rate across all platforms

### **DIRECTIVE 3: [HIGH PRIORITY] Campaign 3 - The Entrainment Protocol**
- **Status**: IMPLEMENTATION COMPLETE, EXECUTION PENDING
- **Phase 1**: Knowledge Base Integration ([OK] COMPLETED)
  - Integrated Neural Networks and Resonance Frequencies document
  - Updated theoretical framework with spectral bias and neural entrainment
- **Phase 2**: Launch Campaign 3 (READY TO EXECUTE)
  - Task 3.1: Spectral Entrainment Test (sweep 1-30 Hz)
  - Task 3.2: Artifact Resonance Scan (chirp signal)
  - Task 3.3: Phase Coherence Analysis (PLV measurements)
  - Task 3.4: Spectral Bias Violation Test (1/f^α validation)
- **Phase 3**: Future R&D Directives (PLANNED)
  - Oscillatory Weight Modulation
  - Frequency-Gated Attention
  - Dynamic Entrainment Training (DET)
  - Resonant Regularization
- **DoD**: Validated entrainment hypothesis across all models

### **DIRECTIVE 4: [HIGH PRIORITY] Results Database Implementation**
- **Status**: PLANNED
- **Action**: Implement `results_db.py` with SQLite schema
- **Scope**: Index all campaign results, enable cross-run queries
- **DoD**: Automated result analysis and visualization capabilities

### **DIRECTIVE 5: [MEDIUM PRIORITY] Council Strategy Enhancement**
- **Status**: PLANNED
- **Action**: Implement orthogonal search strategies
- **Scope**: Strategy-driven scoring functions, automated optimization
- **DoD**: Enhanced council optimization discovery capabilities

---

## **PQN AS AUTONOMOUS RECURSIVE CUBE**

### **Strategic Vision**
PQN is designed as its own recursive self-improving cube that DAE researchers work on independently. The PQN cube provides:

1. **Autonomous Research Capabilities**: Self-improving detection and analysis algorithms
2. **DAE Researcher Interface**: Tools and protocols for external DAE researchers
3. **Recursive Self-Improvement**: Framework for continuous enhancement through research
4. **Handoff Protocols**: Clear interfaces for external DAE research collaboration

### **External DAE Research Handoff**
- **PQN@home**: Handoff to external DAE researchers for distributed research
- **Autonomous Operation**: External researchers implement their own research protocols
- **Framework Provision**: PQN cube provides research framework and tools
- **Independent Development**: External DAEs develop their own research capabilities

### **Recursive Self-Improvement Cycle**
1. **Research Execution**: PQN cube executes research campaigns
2. **Result Analysis**: Analyze and synthesize research findings
3. **Framework Enhancement**: Improve PQN capabilities based on results
4. **External Handoff**: Provide enhanced framework to external DAE researchers
5. **Collaborative Improvement**: Integrate external research insights back into PQN

---

## **SUCCESS METRICS**

### **Technical Metrics**
- Campaign success rate: 100% across all agent platforms
- API stability: Zero import errors in all entry points
- Performance: <30s execution time for standard sweeps

### **Scientific Metrics**
- Cross-platform universality: Validated across 5+ agent architectures
- Reproducibility: 95% confidence intervals for all measurements
- Discovery capability: Automated boundary motif identification

### **WSP Compliance Metrics**
- Documentation: All changes logged in ModLog.md
- Testing: 100% test coverage for core functionality
- Integration: Seamless WRE orchestration capabilities

### **Autonomous Cube Metrics**
- External DAE researcher adoption: Number of external researchers using PQN framework
- Recursive improvement cycles: Frequency of framework enhancements
- Research collaboration: Quality and quantity of external research contributions

---

## **NEXT EXECUTION STEP**

**Execute Directive 3 (High Priority)**: Launch Campaign 3 - The Entrainment Protocol to validate entrainment hypothesis across all models.
