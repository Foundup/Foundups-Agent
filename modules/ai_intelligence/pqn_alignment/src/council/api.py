"""
Council API
- Processes proposal scripts across seeds and aggregates summary scores.
"""
from typing import Tuple, Dict, List
import os
import json


def _get(cfg: Dict, key: str, default):
	return cfg.get(key, default)


def council_run(config: Dict) -> Tuple[str, str]:
	"""
	Run a council cycle over proposal scripts and seeds.
	Expected keys: proposals(list[dict] with 'scripts'), seeds(list[int]), steps, topN
	Returns: (summary_json, archive_json)
	"""
	from modules.ai_intelligence.pqn_alignment.src.sweep.api import rerun_targeted
	from modules.ai_intelligence.pqn_alignment.src.detector.api import run_detector

	proposals: List[Dict] = _get(config, "proposals", [])
	seeds: List[int] = _get(config, "seeds", [0])
	steps = int(_get(config, "steps", 1200))
	out_dir = _get(config, "out_dir", os.path.join("WSP_agentic","tests","pqn_detection","council"))
	os.makedirs(out_dir, exist_ok=True)

	results: List[Dict] = []
	for idx, prop in enumerate(proposals):
		scripts: List[str] = prop.get("scripts", [])
		for scr in scripts:
			# Evaluate one seed via detector to approximate rates; expand as needed
			events_path, metrics_csv = run_detector({
				"script": scr,
				"steps": steps,
				"steps_per_sym": int(_get(config, "steps_per_sym", 120)),
				"dt": float(_get(config, "dt", 0.5/7.05)),
				"out_dir": out_dir,
				"log_csv": f"council_{idx}_{scr.replace('.', 'dot')}.csv",
				"events": f"council_{idx}_{scr.replace('.', 'dot')}.jsonl",
			})
			# Minimal proxy scoring: count lines containing PQN_DETECTED in events
			pqn = 0
			par = 0
			if os.path.exists(events_path):
				with open(events_path, "r", encoding="utf-8") as f:
					for line in f:
						if "PQN_DETECTED" in line:
							pqn += 1
						if "PARADOX_RISK" in line:
							par += 1
			score = 3.0 * pqn - 2.0 * par
			results.append({
				"proposal_idx": idx,
				"author": prop.get("author", "unknown"),
				"script": scr,
				"avg_pqn_per_1k": pqn,  # placeholder; actual normalize by steps in future
				"avg_paradox_per_1k": par,
				"avg_res_hits": 0.0,
				"robust_bonus": 0.0,
				"novel_bonus": 0.0,
				"score": score,
			})

	results.sort(key=lambda r: r["score"], reverse=True)
	topN = int(_get(config, "topN", 5))
	top = results[:topN]

	summary_path = os.path.join(out_dir, "summary.json")
	archive_path = os.path.join(out_dir, "archive.json")
	with open(summary_path, "w", encoding="utf-8") as fs:
		json.dump({"results": results, "top": top}, fs, indent=2)
	with open(archive_path, "w", encoding="utf-8") as fa:
		json.dump({"top_scripts": [r["script"] for r in top]}, fa, indent=2)
	return summary_path, archive_path
