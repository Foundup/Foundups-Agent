# INTERFACE — PQN Alignment

## Public API
- run_detector(config: dict) -> (events_path: str, metrics_csv: str)
- phase_sweep(config: dict) -> (results_csv: str, plot_png: str)
- rerun_targeted(config: dict) -> (out_dir: str)
- council_run(config: dict) -> (summary_json: str, archive_json: str)
- promote(paths: list[str], dst_dir: str) -> None

## Config Keys
- Common: script, steps, steps_per_sym, dt, seed, noise_H, noise_L, out_dir
- Sweep: alphabet, length, plot (bool)
- Council: proposals (list[dict]|paths), seeds (list[int]), dt_scale (list[float]), topN (int)
- Council roles (optional): `roles: [{name: str, bias: str}]` (e.g., maximize PQN, minimize paradox, alternation explorer)

## Return Values
- events_path: file path to JSONL event log
- metrics_csv: file path to CSV metrics
- results_csv: file path to CSV summarizing sweep results
- plot_png: file path to PNG scatter plot if generated
- out_dir: directory containing targeted run outputs
- summary_json: file path to council summary JSON
- archive_json: file path to council archive JSON

## Input Config Schema (YAML/JSON)
Minimal detector config example:
```yaml
script: "^^^&&&#"
steps: 1200
steps_per_sym: 120
dt: 0.5/7.05
seed: 0
noise_H: 0.0
noise_L: 0.0
out_dir: "WSP_agentic/tests/pqn_detection/logs"
```
Sweep config example:
```yaml
alphabet: "^&#."
length: 3
steps: 800
steps_per_sym: 120
dt: 0.5/7.05
plot: true
```
Council config example (minimal):
```yaml
proposals:
  - author: builtin
    type: experiment
    scripts: ["^^^", "^&#", "&&#"]
    sweep:
      dt_scale: [1.0]
seeds: [0,1,2]
steps: 1200
topN: 5
roles:
  - name: ModelA
    bias: maximize PQN
  - name: ModelB
    bias: minimize paradox
  - name: ModelC
    bias: alternation explorer
```

## Output Schemas
Detector events JSONL (one JSON object per line):
- Required fields: `t` (float), `sym` (str), `C` (float), `E` (float), `rnorm` (float), `purity` (float), `S` (float), `detg` (float or null), `det_thr` (float), `flags` (list[str])
- Optional: `peaks` (object), `reso_hit` (tuple/array), `seed` (int), `script_id` (str)

Detector metrics CSV (columns):
- `t,step,sym,C,E,rnorm,purity,S,detg,det_thr,reso_hit_freq,reso_hit_mag,ew_varE,ew_ac1E,ew_dS`

Sweep results CSV (columns):
- `script,steps,pqn,paradox,res_hits,pqn_per_1k,paradox_per_1k,dt,noise_H,noise_L,seed`

Council summary JSON (structure):
```json
{
  "results": [
    {
      "proposal_idx": 0,
      "author": "builtin",
      "script": "^^^",
      "dt_scale": 1.0,
      "avg_pqn_per_1k": 88.3,
      "avg_paradox_per_1k": 0.0,
      "avg_res_hits": 689.0,
      "robust_bonus": 88.3,
      "novel_bonus": 0.5,
      "score": 1387.3
    }
  ],
  "top": [ { "script": "^^^", "score": 1387.3 } ]
}
```

## Error Handling
- ValueError: invalid or missing parameters
- OSError/IOError: file system operations failed
- RuntimeError: execution or promotion failure

## Examples
```python
from modules.ai_intelligence.pqn_alignment import run_detector, phase_sweep

# Detector
events_path, metrics_csv = run_detector({
    "script": "^^^&&&#",
    "steps": 1200,
    "steps_per_sym": 120,
    "dt": 0.5/7.05,
    "out_dir": "WSP_agentic/tests/pqn_detection/logs",
})

# Sweep
results_csv, plot_png = phase_sweep({
    "alphabet": "^&#.",
    "length": 3,
    "steps": 800,
    "steps_per_sym": 120,
    "dt": 0.5/7.05,
    "plot": True,
})
```

## Dependencies
- Python ≥ 3.10
- numpy
- pyyaml (optional, enables YAML config loading)

Install into venv:
```bash
venv\Scripts\pip.exe install numpy pyyaml
```

## Execution Notes
- `phase_sweep` now invokes the repository CLI `WSP_agentic/tests/pqn_detection/pqn_phase_sweep.py` to generate artifacts into `WSP_agentic/tests/pqn_detection/logs/phase_len{N}/`.
- If using YAML configs and pyyaml is not installed, use JSON instead.