"""
Labeling utilities for classifying motifs by stability.
- classify_rows(df, pqn_col, par_col, k) -> dict with top_stable, top_unstable
- Stability heuristic: maximize pqn, minimize paradox; instability: maximize both.
"""
from typing import Dict


def classify_rows(df, pqn_col: str = 'pqn_per_1k', par_col: str = 'paradox_per_1k', k: int = 3) -> Dict[str, list]:
	if df is None or df.empty:
		return {"top_stable": [], "top_unstable": []}
	cols = set(df.columns)
	if pqn_col not in cols and 'pqn_rate' in cols:
		pqn_col = 'pqn_rate'
	if par_col not in cols and 'paradox_rate' in cols:
		par_col = 'paradox_rate'
	if pqn_col not in df.columns or par_col not in df.columns:
		return {"top_stable": [], "top_unstable": []}
	# Stable: sort by high pqn then low paradox
	stable = df.sort_values([pqn_col, par_col], ascending=[False, True]).head(k)
	# Unstable: high pqn and high paradox (descending both)
	unstable = df.sort_values([pqn_col, par_col], ascending=[False, False]).head(k)
	return {
		"top_stable": stable.to_dict(orient='records'),
		"top_unstable": unstable.to_dict(orient='records'),
	}
