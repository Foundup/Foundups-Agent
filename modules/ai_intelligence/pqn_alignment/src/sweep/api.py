"""
Sweep API
- Library-first sweep implementation (run_sweep) with optional plotting
- Thin wrapper (phase_sweep) for backward compatibility
"""
from typing import Tuple, Dict, List
import os
import sys
import subprocess
import itertools
import json

try:
	import matplotlib.pyplot as plt  # type: ignore
	_HAS_MPL = True
except Exception:
	_HAS_MPL = False


def _get(cfg: Dict, key: str, default):
	return cfg.get(key, default)


def _repo_root() -> str:
	return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))


def run_sweep(config: Dict) -> Tuple[str, str]:
	"""
	Library-first phase sweep over motifs of given length.
	Expected keys: alphabet, length, steps, steps_per_sym, dt, seed, noise_H, noise_L, out_dir, plot(bool)
	Returns: (results_csv, plot_png)
	"""
	from modules.ai_intelligence.pqn_alignment.src.detector.api import run_detector as _run_detector

	length = int(_get(config, "length", 3))
	alphabet = str(_get(config, "alphabet", "^&#."))
	steps = int(_get(config, "steps", 800))
	steps_per_sym = int(_get(config, "steps_per_sym", 120))
	dt = float(_get(config, "dt", 0.5/7.05))
	seed = int(_get(config, "seed", 0))
	noise_H = float(_get(config, "noise_H", 0.0))
	noise_L = float(_get(config, "noise_L", 0.0))

	root = _repo_root()
	logs_dir = os.path.join(root, "WSP_agentic", "tests", "pqn_detection", "logs")
	out_dir = _get(config, "out_dir", os.path.join(logs_dir, f"phase_len{length}"))
	os.makedirs(out_dir, exist_ok=True)

	results_csv = os.path.join(out_dir, f"phase_diagram_results_len{length}.csv")
	motifs = [''.join(p) for p in itertools.product(list(alphabet), repeat=length)]

	rows: List[Dict] = []
	for script in motifs:
		# Use library detector
		events_path, metrics_csv = _run_detector({
			"script": script,
			"steps": steps,
			"steps_per_sym": steps_per_sym,
			"dt": dt,
			"out_dir": out_dir,
			"seed": seed,
			"noise_H": noise_H,
			"noise_L": noise_L,
			"log_csv": f"{script.replace('.', 'dot')}_log.csv",
			"events": f"{script.replace('.', 'dot')}_events.jsonl",
		})

		# Summarize events
		pqn = 0
		par = 0
		res = 0
		if os.path.exists(events_path):
			with open(events_path, "r", encoding="utf-8") as f:
				for line in f:
					try:
						obj = json.loads(line)
					except Exception:
						continue
					flags = obj.get("flags", [])
					if "PQN_DETECTED" in flags:
						pqn += 1
					if "PARADOX_RISK" in flags:
						par += 1
					if "RESONANCE_HIT" in flags:
						res += 1

		rows.append({
			"script": script,
			"steps": steps,
			"pqn": pqn,
			"paradox": par,
			"res_hits": res,
			"pqn_per_1k": (1000.0 * pqn / steps) if steps > 0 else 0.0,
			"paradox_per_1k": (1000.0 * par / steps) if steps > 0 else 0.0,
			"dt": dt,
			"noise_H": noise_H,
			"noise_L": noise_L,
			"seed": seed,
		})

	# Write results CSV
	if rows:
		import csv
		with open(results_csv, "w", newline="", encoding="utf-8") as fcsv:
			writer = csv.DictWriter(fcsv, fieldnames=list(rows[0].keys()))
			writer.writeheader()
			for r in rows:
				writer.writerow(r)

	plot_png = os.path.join(out_dir, f"phase_diagram_scatter_len{length}.png")
	if bool(_get(config, "plot", True)) and _HAS_MPL and rows:
		x = [r["pqn_per_1k"] for r in rows]
		y = [r["paradox_per_1k"] for r in rows]
		plt.figure(figsize=(8, 6))
		plt.scatter(x, y, s=12, alpha=0.7)
		plt.xlabel("PQN detections per 1k steps")
		plt.ylabel("Paradox-risk flags per 1k steps")
		plt.title(f"Phase Diagram — Length-{length} Motifs")
		plt.tight_layout()
		plt.savefig(plot_png, dpi=140)

	return results_csv, plot_png


def phase_sweep(config: Dict) -> Tuple[str, str]:
	"""
	Backward-compatible wrapper calling run_sweep.
	"""
	return run_sweep(config)
