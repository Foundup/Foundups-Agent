"""
Analyze a run directory and print a concise summary.
Expected files: results.csv (required), config.yml (optional)
Outputs: prints top stable/unstable motifs if present.
"""
import os
from typing import Tuple


def analyze_run(run_dir: str) -> Tuple[int, int]:
	"""
	Analyze the given run directory and return (num_rows, num_features_found).
	"""
	results_csv = os.path.join(run_dir, 'results.csv')
	if not os.path.exists(results_csv):
		raise FileNotFoundError(f"results.csv not found in {run_dir}")
	import pandas as pd  # local import
	from modules.ai_intelligence.pqn_alignment.src.labeling import classify_rows
	try:
		df = pd.read_csv(results_csv)
	except Exception as e:
		raise RuntimeError(f"failed to read results.csv: {e}")
	labels = classify_rows(df)
	# Print concise summary
	print("Top stable (high PQN, low paradox):")
	for row in labels.get("top_stable", []):
		print(f"- {row.get('script','?')} pqn={row.get('pqn_per_1k',row.get('pqn_rate'))} par={row.get('paradox_per_1k',row.get('paradox_rate'))}")
	print("Top unstable (high PQN, high paradox):")
	for row in labels.get("top_unstable", []):
		print(f"- {row.get('script','?')} pqn={row.get('pqn_per_1k',row.get('pqn_rate'))} par={row.get('paradox_per_1k',row.get('paradox_rate'))}")
	return (len(df), sum(1 for _ in labels.get("top_stable", [])) + sum(1 for _ in labels.get("top_unstable", [])))
