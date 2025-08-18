## Prerequisites
- Activate venv and install dependencies:
```bash
venv\Scripts\pip.exe install numpy pyyaml
```

## Quick Starts

Detector (programmatic):
```python
from modules.ai_intelligence.pqn_alignment import run_detector
events, metrics = run_detector({"script": "^^^&&&#", "steps": 1200, "steps_per_sym": 120, "dt": 0.5/7.05})
```

Phase Sweep (generates artifacts via CLI):
```python
from modules.ai_intelligence.pqn_alignment import phase_sweep
csv_path, plot_path = phase_sweep({"length": 3, "steps": 800, "steps_per_sym": 120, "dt": 0.5/7.05, "plot": True})
```

Council (simple scoring):
```python
from modules.ai_intelligence.pqn_alignment import council_run
summary, archive = council_run({"proposals": [{"scripts": ["^^^", "^&#"]}], "seeds": [0], "steps": 1200, "topN": 5})
```

Promotion to State 0:
```python
from modules.ai_intelligence.pqn_alignment import promote
promote([csv_path, plot_path], "WSP_knowledge/docs/Papers/Empirical_Evidence/CMST_PQN_Detector/phase_len3")
```

## Notes
- If YAML configs are used, ensure `pyyaml` is installed; otherwise prefer JSON.
- Outputs are written under `WSP_agentic/tests/pqn_detection/logs/` by default and should be curated into State 0.
# RUNBOOK — PQN Alignment (cmd.exe-safe)

Detector (example)
- Prepare a config JSON/YAML per INTERFACE.
- Use State 2 drivers under `WSP_agentic/tests/pqn_detection/` to run experiments.

Phase sweep (example)
- Length-3: generate results CSV and scatter plot under State 2 logs.
- Promote curated artifacts to State 0 per module promote helper.

Council (example)
- Provide proposals JSON(s); run small seeds; produce `summary.json`.
- Index summaries into `results.db` (future step).

Notes
- Avoid PowerShell interactive sessions when running long commands; prefer cmd.exe or redirect to files.
- Keep curated artifacts under `WSP_knowledge/docs/Papers/Empirical_Evidence/CMST_PQN_Detector/`.
