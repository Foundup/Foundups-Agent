"""
Detector API
- Adapts to WSP_agentic/tests/pqn_detection/cmst_pqn_detector_v2.py
"""
from typing import Tuple, Dict
import os


def _get(cfg: Dict, key: str, default):
	v = cfg.get(key, default)
	return v


def run_detector(config: Dict) -> Tuple[str, str]:
	"""
	Run the PQN detector with the given config.
	Expected keys: script, steps, steps_per_sym, dt, out_dir (optional)
	Returns: (events_path, metrics_csv)
	"""
	# Resolve paths
	out_dir = _get(config, "out_dir", os.path.join("WSP_agentic","tests","pqn_detection","logs"))
	os.makedirs(out_dir, exist_ok=True)
	metrics_csv = os.path.join(out_dir, _get(config, "log_csv", "detector_metrics.csv"))
	events_path = os.path.join(out_dir, _get(config, "events", "detector_events.jsonl"))

	# Import runner lazily
	from WSP_agentic.tests.pqn_detection import cmst_pqn_detector_v2 as v2

	# Map config to runner
	v2.run(
		log_csv_path=metrics_csv,
		events_path=events_path,
		script=_get(config, "script", "^^^&&&#^&##"),
		steps=int(_get(config, "steps", 1200)),
		steps_per_sym=int(_get(config, "steps_per_sym", 120)),
		base_dt=float(_get(config, "dt", 0.5/7.05)),
		geom_win=int(_get(config, "geom_win", 64)),
		reso_win=int(_get(config, "reso_win", 512)),
		reso_tol=float(_get(config, "reso_tol", 0.05)),
		consec=int(_get(config, "consec", 10)),
		kE=float(_get(config, "kE", 0.35)),
		kA=float(_get(config, "kA", 0.25)),
		gD=float(_get(config, "gD", 0.08)),
		seed=int(_get(config, "seed", 0)),
	)
	return events_path, metrics_csv
